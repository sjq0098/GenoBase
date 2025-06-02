from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.forms import SearchForm, SpeciesForm, GeneForm, ProteinForm, PublicationForm, ExperimentalDataForm
from app.models import Species, Genes, Proteins, Publications, Experimental_Data, Gene_Publications, Users
from sqlalchemy import or_, func, text

@bp.route('/')
@bp.route('/index')
def index():
    # 获取一些统计数据
    stats = {
        'species_count': Species.query.count(),
        'gene_count': Genes.query.count(),
        'protein_count': Proteins.query.count(),
        'publication_count': Publications.query.count(),
        'experiment_count': Experimental_Data.query.count()
    }
    
    # 获取最新添加的数据
    latest_genes = Genes.query.order_by(Genes.created_at.desc()).limit(5).all()
    latest_proteins = Proteins.query.order_by(Proteins.created_at.desc()).limit(5).all()
    latest_publications = Publications.query.order_by(Publications.created_at.desc()).limit(5).all()
    
    return render_template('main/index.html', title='首页', stats=stats, 
                           latest_genes=latest_genes, latest_proteins=latest_proteins, 
                           latest_publications=latest_publications)

@bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    results = []
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data or request.args.get('query')
        category = form.category.data or request.args.get('category', 'all')
        page = request.args.get('page', 1, type=int)
        
        if category == 'gene' or category == 'all':
            genes = Genes.query.filter(
                or_(
                    Genes.gene_name.contains(query),
                    Genes.gene_symbol.contains(query)
                )
            ).all()
            results.extend([{'type': 'gene', 'data': gene} for gene in genes])
        
        if category == 'protein' or category == 'all':
            proteins = Proteins.query.filter(
                or_(
                    Proteins.protein_name.contains(query),
                    Proteins.uniprot_id.contains(query)
                )
            ).all()
            results.extend([{'type': 'protein', 'data': protein} for protein in proteins])
        
        if category == 'species' or category == 'all':
            species = Species.query.filter(
                or_(
                    Species.scientific_name.contains(query),
                    Species.common_name.contains(query),
                    Species.taxonomy_id.contains(query)
                )
            ).all()
            results.extend([{'type': 'species', 'data': sp} for sp in species])
        
        if category == 'publication' or category == 'all':
            publications = Publications.query.filter(
                or_(
                    Publications.title.contains(query),
                    Publications.authors.contains(query),
                    Publications.journal.contains(query),
                    Publications.doi.contains(query)
                )
            ).all()
            results.extend([{'type': 'publication', 'data': pub} for pub in publications])
        
        # 分页
        total = len(results)
        per_page = current_app.config['POSTS_PER_PAGE']
        start = (page - 1) * per_page
        end = min(start + per_page, total)
        paginated_results = results[start:end]
        
        return render_template('main/search_results.html', title='搜索结果',
                               form=form, results=paginated_results, query=query,
                               category=category, total=total, page=page,
                               per_page=per_page, total_pages=(total + per_page - 1) // per_page)
    
    return render_template('main/search.html', title='搜索', form=form)

# 物种相关路由
@bp.route('/species')
def species_list():
    page = request.args.get('page', 1, type=int)
    species = Species.query.order_by(Species.scientific_name).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('main/species_list.html', title='物种列表', species=species)

@bp.route('/species/<int:id>')
def species_detail(id):
    species = Species.query.get_or_404(id)
    genes = species.genes.all()
    return render_template('main/species_detail.html', title=species.scientific_name, species=species, genes=genes)

# 基因相关路由
@bp.route('/genes')
def gene_list():
    page = request.args.get('page', 1, type=int)
    genes = Genes.query.order_by(Genes.gene_name).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('main/gene_list.html', title='基因列表', genes=genes)

@bp.route('/genes/<int:id>')
def gene_detail(id):
    gene = Genes.query.get_or_404(id)
    proteins = gene.proteins.all()
    publications = gene.publications
    experiments = gene.experimental_data.all()
    return render_template('main/gene_detail.html', title=gene.gene_name, 
                           gene=gene, proteins=proteins, 
                           publications=publications, experiments=experiments)

# 蛋白质相关路由
@bp.route('/proteins')
def protein_list():
    page = request.args.get('page', 1, type=int)
    proteins = Proteins.query.order_by(Proteins.protein_name).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('main/protein_list.html', title='蛋白质列表', proteins=proteins)

@bp.route('/proteins/<int:id>')
def protein_detail(id):
    protein = Proteins.query.get_or_404(id)
    return render_template('main/protein_detail.html', title=protein.protein_name, protein=protein)

# 文献相关路由
@bp.route('/publications')
def publication_list():
    page = request.args.get('page', 1, type=int)
    publications = Publications.query.order_by(Publications.publication_year.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('main/publication_list.html', title='文献列表', publications=publications)

@bp.route('/publications/<int:id>')
def publication_detail(id):
    publication = Publications.query.get_or_404(id)
    genes = publication.genes
    experiments = publication.experimental_data.all()
    return render_template('main/publication_detail.html', title=publication.title, 
                           publication=publication, genes=genes, experiments=experiments)

# 实验数据相关路由
@bp.route('/experiments')
def experiment_list():
    page = request.args.get('page', 1, type=int)
    experiments = Experimental_Data.query.order_by(Experimental_Data.created_at.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('main/experiment_list.html', title='实验数据列表', experiments=experiments)

@bp.route('/experiments/<int:id>')
def experiment_detail(id):
    experiment = Experimental_Data.query.get_or_404(id)
    return render_template('main/experiment_detail.html', title=experiment.experiment_type, experiment=experiment) 

@bp.route('/gene_activity')
def gene_activity():
    result = db.session.execute(text(
        "SELECT gene_id, gene_name, species_name, publication_count, experiment_count, activity_score "
        "FROM GeneResearchActivity ORDER BY activity_score DESC LIMIT 20"
    ))
    activity_data = [dict(row._mapping) for row in result]
    return render_template('main/gene_activity.html', activity_data=activity_data)

@bp.route('/publications/add', methods=['GET', 'POST'])
@login_required
def add_publication():
    form = PublicationForm()
    # 获取所有基因作为选项，使用正确的gene_id属性
    form.gene_ids.choices = [(g.gene_id, f"{g.gene_name} ({g.gene_symbol})") for g in Genes.query.order_by(Genes.gene_name).all()]
    
    if form.validate_on_submit():
        publication = Publications(
            title=form.title.data,
            authors=form.authors.data,
            journal=form.journal.data,
            publication_year=form.publication_year.data,
            doi=form.doi.data
        )
        db.session.add(publication)
        
        # 处理基因关联
        if form.gene_ids.data:
            for gene_id in form.gene_ids.data:
                gene = Genes.query.get(gene_id)
                if gene:
                    publication.genes.append(gene)
        
        db.session.commit()
        flash('文献添加成功！', 'success')
        return redirect(url_for('main.publication_list'))
    
    return render_template('admin/publication_form.html', title='添加文献', form=form)

@bp.route('/publications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_publication(id):
    publication = Publications.query.get_or_404(id)
    form = PublicationForm()
    # 获取所有基因作为选项，使用正确的gene_id属性
    form.gene_ids.choices = [(g.gene_id, f"{g.gene_name} ({g.gene_symbol})") for g in Genes.query.order_by(Genes.gene_name).all()]
    
    if form.validate_on_submit():
        publication.title = form.title.data
        publication.authors = form.authors.data
        publication.journal = form.journal.data
        publication.publication_year = form.publication_year.data
        publication.doi = form.doi.data
        
        # 更新基因关联
        # 移除所有现有关联
        Gene_Publications.query.filter_by(publication_id=publication.publication_id).delete()
        
        # 添加新的关联
        if form.gene_ids.data:
            for gene_id in form.gene_ids.data:
                gene = Genes.query.get(gene_id)
                if gene:
                    publication.genes.append(gene)
        
        db.session.commit()
        flash('文献更新成功！', 'success')
        return redirect(url_for('main.publication_detail', id=publication.publication_id))
    
    # 预填充表单数据
    elif request.method == 'GET':
        form.title.data = publication.title
        form.authors.data = publication.authors
        form.journal.data = publication.journal
        form.publication_year.data = publication.publication_year
        form.doi.data = publication.doi
        form.gene_ids.data = [gene.gene_id for gene in publication.genes]
    
    return render_template('admin/publication_form.html', title='编辑文献', form=form)

@bp.route('/profile')
@login_required
def user_profile():
    # 如果需要，可以从数据库加载更详细的用户信息
    # user = Users.query.filter_by(username=current_user.username).first_or_404()
    return render_template('main/user_profile.html', title='用户详情', user=current_user)