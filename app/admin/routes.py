from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.forms import SpeciesForm, GeneForm, ProteinForm, PublicationForm, ExperimentalDataForm, SequenceUploadForm
from app.models import Species, Genes, Proteins, Publications, Experimental_Data, Gene_Publications, Users, UserRoleInfo, GeneProteinCountBySpecies
from sqlalchemy import func, text
import re
from Bio import SeqIO
from io import StringIO
from sqlalchemy.exc import IntegrityError, DatabaseError

def check_admin_access():
    """检查用户是否有管理员权限"""
    if not current_user.is_authenticated:
        abort(401)  # 未认证
    if not (current_user.is_manager() or current_user.is_creator()):
        abort(403)  # 无权限

@bp.route('/')
@login_required
def admin_index():
    check_admin_access()
    return render_template('admin/index.html', title='管理面板')

# 用户管理路由
@bp.route('/users')
@login_required
def user_list():
    check_admin_access()
    if current_user.is_manager() and current_user.manager.access_level != 'full':
        flash('您没有访问用户列表的权限')
        return redirect(url_for('admin.admin_index'))
    
    users = UserRoleInfo.query.all()
    return render_template('admin/user_list.html', title='用户管理', users=users)

@bp.route('/users/<int:id>/toggle_active')
@login_required
def toggle_user_active(id):
    check_admin_access()
    if current_user.is_manager() and current_user.manager.access_level != 'full':
        flash('您没有修改用户状态的权限')
        return redirect(url_for('admin.user_list'))
    
    user = Users.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'用户 {user.username} 状态已更新')
    return redirect(url_for('admin.user_list'))

# 物种管理路由
@bp.route('/species/add', methods=['GET', 'POST'])
@login_required
def add_species():
    check_admin_access()
    form = SpeciesForm()
    if form.validate_on_submit():
        species = Species(
            scientific_name=form.scientific_name.data,
            common_name=form.common_name.data,
            taxonomy_id=form.taxonomy_id.data,
            description=form.description.data
        )
        db.session.add(species)
        db.session.commit()
        flash('物种添加成功')
        return redirect(url_for('main.species_detail', id=species.species_id))
    return render_template('admin/species_form.html', title='添加物种', form=form)

@bp.route('/species/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_species(id):
    check_admin_access()
    species = Species.query.get_or_404(id)
    form = SpeciesForm()
    if form.validate_on_submit():
        try:
            result = db.session.execute(
                text('CALL UpdateSpeciesInfo(:species_id, :scientific_name, :common_name, :description)'),
                {
                    'species_id': id,
                    'scientific_name': form.scientific_name.data,
                    'common_name': form.common_name.data,
                    'description': form.description.data
                }
            )
            # 只读取第一个结果集
            try:
                for row in result:
                    flash(row[0], 'success')
            except Exception as e:
                if "Commands out of sync" not in str(e):
                    flash(f'发生未知错误：{str(e)}', 'error')
            db.session.commit()
            return redirect(url_for('main.species_detail', id=species.species_id))

        except DatabaseError as e:
            db.session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'Species ID not found' in error_msg:
                flash('错误：找不到指定的物种ID', 'error')
            else:
                flash(f'数据库错误：{error_msg}', 'error')
            return render_template('admin/species_form.html', title='编辑物种', form=form)
        except Exception as e:
            db.session.rollback()
            # 只在不是"Commands out of sync"时才显示
            if "Commands out of sync" not in str(e):
                flash(f'发生未知错误：{str(e)}', 'error')
            return redirect(url_for('main.species_detail', id=species.species_id))
            
    elif request.method == 'GET':
        form.scientific_name.data = species.scientific_name
        form.common_name.data = species.common_name
        form.taxonomy_id.data = species.taxonomy_id
        form.description.data = species.description
    return render_template('admin/species_form.html', title='编辑物种', form=form)

from sqlalchemy import text

@bp.route('/species/<int:id>/delete', methods=['POST'])
@login_required
def delete_species(id):
    check_admin_access()
    if current_user.is_manager() and current_user.manager.access_level != 'full':
        flash('您没有删除物种的权限')
        return redirect(url_for('main.species_detail', id=id))

    # 确保物种存在，否则 404
    Species.query.get_or_404(id)

    try:
        # 直接调用存储过程（当前 Session 已经有事务，这里直接 execute）
        db.session.execute(
            text("CALL DeleteSpeciesWithRelatedData(:sid)"),
            {"sid": id}
        )
        # 存储过程内部要么 commit，要么因 SIGNAL 抛异常
        # 这里只再做一次 commit，把实体 Session 的事务提交
        db.session.commit()
    except Exception as e:
        # 如果有任何异常，回滚当前 Session 的事务
        db.session.rollback()
        flash(f'删除失败：{str(e)}')
        return redirect(url_for('main.species_detail', id=id))

    flash('物种及其所有关联数据已删除')
    return redirect(url_for('main.species_list'))


# 基因管理路由
@bp.route('/genes/add', methods=['GET', 'POST'])
@login_required
def add_gene():
    check_admin_access()
    form = GeneForm()
    form.species_id.choices = [(s.species_id, s.scientific_name) for s in Species.query.order_by(Species.scientific_name).all()]
    
    if form.validate_on_submit():
        # 清理序列
        sequence = re.sub(r'\s+', '', form.sequence.data)
        
        gene = Genes(
            gene_name=form.gene_name.data,
            gene_symbol=form.gene_symbol.data,
            sequence=sequence,
            chromosome=form.chromosome.data,
            start_position=form.start_position.data,
            end_position=form.end_position.data,
            strand=form.strand.data,
            species_id=form.species_id.data
        )
        db.session.add(gene)
        db.session.commit()
        flash('基因添加成功')
        return redirect(url_for('main.gene_detail', id=gene.gene_id))
    return render_template('admin/gene_form.html', title='添加基因', form=form)

@bp.route('/genes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_gene(id):
    check_admin_access()
    gene = Genes.query.get_or_404(id)
    form = GeneForm()
    form.species_id.choices = [(s.species_id, s.scientific_name) for s in Species.query.order_by(Species.scientific_name).all()]
    
    if form.validate_on_submit():
        # 清理序列
        sequence = re.sub(r'\s+', '', form.sequence.data)
        
        # 如果基因名称发生变化，调用存储过程
        if gene.gene_name != form.gene_name.data:
            try:
                # 调用存储过程更新基因名称和关联的蛋白质信息
                result = db.session.execute(
                    text('CALL UpdateGeneAndProteinInfo(:gene_id, :new_gene_name)'),
                    {'gene_id': gene.gene_id, 'new_gene_name': form.gene_name.data}
                )
                db.session.commit()
                
                # 获取存储过程的返回结果
                for row in result:
                    flash(row[0], 'success')
                    
            except DatabaseError as e:
                db.session.rollback()
                error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                if 'Gene ID not found' in error_msg:
                    flash('错误：找不到指定的基因ID', 'error')
                elif 'Failed to update gene' in error_msg:
                    flash('错误：更新基因失败', 'error')
                else:
                    flash(f'数据库错误：{error_msg}', 'error')
                return render_template('admin/gene_form.html', title='编辑基因', form=form)
            except Exception as e:
                db.session.rollback()
                flash(f'发生未知错误：{str(e)}', 'error')
                return render_template('admin/gene_form.html', title='编辑基因', form=form)
        
        # 更新其他字段
        try:
            gene.gene_symbol = form.gene_symbol.data
            gene.sequence = sequence
            gene.chromosome = form.chromosome.data
            gene.start_position = form.start_position.data
            gene.end_position = form.end_position.data
            gene.strand = form.strand.data
            gene.species_id = form.species_id.data
            
            db.session.commit()
            flash('基因信息已更新', 'success')
            return redirect(url_for('main.gene_detail', id=gene.gene_id))
        except Exception as e:
            db.session.rollback()
            flash(f'更新基因信息时出错: {str(e)}', 'error')
    elif request.method == 'GET':
        form.gene_name.data = gene.gene_name
        form.gene_symbol.data = gene.gene_symbol
        form.sequence.data = gene.sequence
        form.chromosome.data = gene.chromosome
        form.start_position.data = gene.start_position
        form.end_position.data = gene.end_position
        form.strand.data = gene.strand
        form.species_id.data = gene.species_id
    return render_template('admin/gene_form.html', title='编辑基因', form=form)

@bp.route('/genes/<int:id>/delete', methods=['POST'])
@login_required
def delete_gene(id):
    check_admin_access()
    if current_user.is_manager() and current_user.manager.access_level != 'full':
        flash('您没有删除基因的权限')
        return redirect(url_for('main.gene_detail', id=id))
    
    gene = Genes.query.get_or_404(id)
    db.session.delete(gene)
    db.session.commit()
    flash('基因已删除')
    return redirect(url_for('main.gene_list'))

# 蛋白质管理路由
@bp.route('/proteins/add', methods=['GET', 'POST'])
@login_required
def add_protein():
    check_admin_access()
    form = ProteinForm()
    
    # 获取所有基因作为选项
    form.gene_id.choices = [
        (g.gene_id, f"{g.gene_name} ({g.gene_symbol or ''}) - ID: {g.gene_id}")
        for g in Genes.query.order_by(Genes.gene_name).all()
    ]

    if form.validate_on_submit():
        try:
            sequence = re.sub(r'\s+', '', form.amino_acid_sequence.data)
            protein = Proteins(
                protein_name=form.protein_name.data,
                uniprot_id=form.uniprot_id.data,
                amino_acid_sequence=sequence,
                gene_id=form.gene_id.data
            )
            db.session.add(protein)
            db.session.commit()
            flash('蛋白质添加成功', 'success')
            return redirect(url_for('main.protein_detail', id=protein.protein_id))
        except (IntegrityError, DatabaseError) as e:
            db.session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            # 检查是否为触发器报错
            if 'Cannot add protein: Associated gene_id does not exist' in error_msg:
                flash('无法添加蛋白质：所填基因ID不存在，已被数据库触发器拦截。', 'danger')
            else:
                flash(f'数据库错误：{error_msg}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'发生未知错误：{str(e)}', 'danger')
    return render_template('admin/protein_form.html', title='添加蛋白质', form=form)

@bp.route('/proteins/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_protein(id):
    check_admin_access()
    protein = Proteins.query.get_or_404(id)
    form = ProteinForm()
    
    # 获取所有基因作为选项
    form.gene_id.choices = [
        (g.gene_id, f"{g.gene_name} ({g.gene_symbol or ''})")
        for g in Genes.query.order_by(Genes.gene_name).all()
    ]

    if form.validate_on_submit():
        try:
            # 清理序列中的空白字符
            sequence = re.sub(r'\s+', '', form.amino_acid_sequence.data)
            
            # 检查关联的基因是否存在
            gene = Genes.query.get(form.gene_id.data)
            if not gene:
                flash('选择的基因不存在', 'error')
                return render_template('admin/protein_form.html', title='编辑蛋白质', form=form)

            # 更新蛋白质信息
            protein.protein_name = form.protein_name.data
            protein.uniprot_id = form.uniprot_id.data
            protein.amino_acid_sequence = sequence
            protein.gene_id = form.gene_id.data
            
            db.session.commit()
            flash('蛋白质信息已更新', 'success')
            return redirect(url_for('main.protein_detail', id=protein.protein_id))

        except IntegrityError as e:
            db.session.rollback()
            # 处理唯一性约束违反
            if 'uniprot_id' in str(e.orig):
                flash('UniProt ID已被其他蛋白质使用', 'error')
            elif 'protein_name' in str(e.orig):
                flash('蛋白质名称已被其他蛋白质使用', 'error')
            else:
                flash('数据库错误：可能违反了唯一性约束', 'error')
            return render_template('admin/protein_form.html', title='编辑蛋白质', form=form)
            
        except DatabaseError as e:
            db.session.rollback()
            # 处理触发器错误
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'trigger' in error_msg.lower():
                flash(f'触发器验证失败：{error_msg}', 'error')
            else:
                flash(f'数据库错误：{error_msg}', 'error')
            return render_template('admin/protein_form.html', title='编辑蛋白质', form=form)
            
        except Exception as e:
            db.session.rollback()
            flash(f'发生未知错误：{str(e)}', 'error')
            return render_template('admin/protein_form.html', title='编辑蛋白质', form=form)

    elif request.method == 'GET':
        # 预填充表单数据
        form.protein_name.data = protein.protein_name
        form.uniprot_id.data = protein.uniprot_id
        form.amino_acid_sequence.data = protein.amino_acid_sequence
        form.gene_id.data = protein.gene_id

    return render_template('admin/protein_form.html', title='编辑蛋白质', form=form)

@bp.route('/proteins/<int:id>/delete', methods=['POST'])
@login_required
def delete_protein(id):
    check_admin_access()
    protein = Proteins.query.get_or_404(id)
    db.session.delete(protein)
    db.session.commit()
    flash('蛋白质已删除')
    return redirect(url_for('main.protein_list'))

# 文献管理路由
@bp.route('/publications/add', methods=['GET', 'POST'])
@login_required
def add_publication():
    check_admin_access()
    form = PublicationForm()
    
    if form.validate_on_submit():
        publication = Publications(
            title=form.title.data,
            authors=form.authors.data,
            journal=form.journal.data,
            publication_year=form.publication_year.data,
            doi=form.doi.data
        )
        db.session.add(publication)
        db.session.commit()
        flash('文献添加成功')
        return redirect(url_for('main.publication_detail', id=publication.publication_id))
    return render_template('admin/publication_form.html', title='添加文献', form=form)

@bp.route('/publications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_publication(id):
    check_admin_access()
    publication = Publications.query.get_or_404(id)
    form = PublicationForm()
    
    if form.validate_on_submit():
        publication.title = form.title.data
        publication.authors = form.authors.data
        publication.journal = form.journal.data
        publication.publication_year = form.publication_year.data
        publication.doi = form.doi.data
        
        db.session.commit()
        flash('文献信息已更新')
        return redirect(url_for('main.publication_detail', id=publication.publication_id))
    elif request.method == 'GET':
        form.title.data = publication.title
        form.authors.data = publication.authors
        form.journal.data = publication.journal
        form.publication_year.data = publication.publication_year
        form.doi.data = publication.doi
    return render_template('admin/publication_form.html', title='编辑文献', form=form)

@bp.route('/publications/<int:id>/delete', methods=['POST'])
@login_required
def delete_publication(id):
    check_admin_access()
    publication = Publications.query.get_or_404(id)
    
    try:
        # 删除文献相关的所有关联
        Gene_Publications.query.filter_by(publication_id=id).delete()
        Experimental_Data.query.filter_by(publication_id=id).delete()
        
        # 删除文献本身
        db.session.delete(publication)
        db.session.commit()
        flash('文献已成功删除')
    except Exception as e:
        db.session.rollback()
        flash('删除文献时发生错误')
    
    # 获取来源页面
    referrer = request.referrer
    if referrer and 'publications' in referrer:
        # 如果是从文献列表页面来的，返回列表页
        return redirect(url_for('main.publication_list'))
    else:
        # 如果是从其他页面来的，返回首页
        return redirect(url_for('main.index'))

# 实验数据管理路由
@bp.route('/experiments/add', methods=['GET', 'POST'])
@login_required
def add_experiment():
    check_admin_access()
    form = ExperimentalDataForm()
    form.gene_id.choices = [(0, '-- 不关联基因 --')] + [(g.gene_id, f"{g.gene_name} ({g.gene_symbol})") for g in Genes.query.order_by(Genes.gene_name).all()]
    form.publication_id.choices = [(0, '-- 不关联文献 --')] + [(p.publication_id, p.title) for p in Publications.query.order_by(Publications.title).all()]
    
    if form.validate_on_submit():
        try:
            gene_id = form.gene_id.data if form.gene_id.data else None
            # 这里不强制检查 gene_id 是否存在，让触发器兜底
            experiment = Experimental_Data(
                experiment_type=form.experiment_type.data,
                conditions=form.conditions.data,
                results=form.results.data,
                gene_id=gene_id,
                publication_id=form.publication_id.data if form.publication_id.data != 0 else None
            )
            db.session.add(experiment)
            db.session.commit()
            flash('实验数据添加成功', 'success')
            return redirect(url_for('main.experiment_detail', id=experiment.experiment_id))
        except (IntegrityError, DatabaseError) as e:
            db.session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'Cannot add experiment: Associated gene_id does not exist' in error_msg:
                flash('无法添加实验数据：所填基因ID不存在，已被数据库触发器拦截。', 'danger')
            else:
                flash(f'数据库错误：{error_msg}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'发生未知错误：{str(e)}', 'danger')
    return render_template('admin/experiment_form.html', title='添加实验数据', form=form)

@bp.route('/experiments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_experiment(id):
    check_admin_access()
    experiment = Experimental_Data.query.get_or_404(id)
    form = ExperimentalDataForm(obj=experiment)
    if form.validate_on_submit():
        try:
            gene_id = form.gene_id.data if form.gene_id.data else None
            # 更新字段
            experiment.gene_id = gene_id
            # ... 其他字段赋值 ...
            db.session.commit()
            flash('实验数据已更新', 'success')
            return redirect(url_for('main.experiment_detail', id=experiment.experiment_id))
        except (IntegrityError, DatabaseError) as e:
            db.session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'Cannot add experiment: Associated gene_id does not exist' in error_msg:
                flash('无法更新实验数据：所填基因ID不存在，已被数据库触发器拦截。', 'danger')
            else:
                flash(f'数据库错误：{error_msg}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'发生未知错误：{str(e)}', 'danger')
    elif request.method == 'GET':
        # 预填充表单
        form.gene_id.data = experiment.gene_id
        # ... 其他字段 ...
    return render_template('admin/experiment_form.html', title='编辑实验数据', form=form)

@bp.route('/experiments/<int:id>/delete', methods=['POST'])
@login_required
def delete_experiment(id):
    check_admin_access()
    experiment = Experimental_Data.query.get_or_404(id)
    db.session.delete(experiment)
    db.session.commit()
    flash('实验数据已删除')
    return redirect(url_for('main.experiment_list'))

# 基因-文献关联管理
@bp.route('/gene_publications/add', methods=['GET', 'POST'])
@login_required
def add_gene_publication():
    check_admin_access()
    gene_id = request.args.get('gene_id', type=int)
    publication_id = request.args.get('publication_id', type=int)
    
    if request.method == 'POST':
        gene_id = request.form.get('gene_id', type=int)
        publication_id = request.form.get('publication_id', type=int)
        
        if not gene_id or not publication_id:
            flash('基因ID和文献ID是必须的')
            return redirect(url_for('admin.admin_index'))
        
        # 检查是否已存在该关联
        existing = Gene_Publications.query.filter_by(gene_id=gene_id, publication_id=publication_id).first()
        if existing:
            flash('该关联已存在')
            return redirect(url_for('main.gene_detail', id=gene_id))
        
        # 添加关联
        association = Gene_Publications(gene_id=gene_id, publication_id=publication_id)
        db.session.add(association)
        db.session.commit()
        flash('基因-文献关联已添加')
        
        # 重定向到合适的页面
        if request.args.get('from_gene'):
            return redirect(url_for('main.gene_detail', id=gene_id))
        else:
            return redirect(url_for('main.publication_detail', id=publication_id))
    
    # GET 请求处理
    genes = Genes.query.order_by(Genes.gene_name).all()
    publications = Publications.query.order_by(Publications.title).all()
    
    return render_template('admin/gene_publication_form.html', title='添加基因-文献关联',
                          genes=genes, publications=publications,
                          selected_gene_id=gene_id, selected_publication_id=publication_id)

@bp.route('/gene_publications/delete', methods=['POST'])
@login_required
def delete_gene_publication():
    check_admin_access()
    gene_id = request.form.get('gene_id', type=int)
    publication_id = request.form.get('publication_id', type=int)
    
    if not gene_id or not publication_id:
        flash('基因ID和文献ID是必须的')
        return redirect(url_for('admin.admin_index'))
    
    # 删除关联
    association = Gene_Publications.query.filter_by(gene_id=gene_id, publication_id=publication_id).first_or_404()
    db.session.delete(association)
    db.session.commit()
    flash('基因-文献关联已删除')
    
    # 重定向到合适的页面
    if request.form.get('from_gene'):
        return redirect(url_for('main.gene_detail', id=gene_id))
    else:
        return redirect(url_for('main.publication_detail', id=publication_id))

@bp.route('/gene_protein_count')
@login_required
def gene_protein_count():
    check_admin_access()
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 每页显示20条，可根据需要调整
    pagination = GeneProteinCountBySpecies.query.paginate(page=page, per_page=per_page, error_out=False)
    records = pagination.items
    return render_template(
        'admin/gene_protein_count.html',
        title='基因-物种-蛋白质数量统计',
        records=records,
        pagination=pagination
    ) 
    
