from flask import jsonify, request, current_app, abort
from flask_login import current_user
from app import db
from app.api import bp
from app.models import Species, Genes, Proteins, Publications, Experimental_Data, Gene_Publications, Users
from sqlalchemy import or_, func
import json

# API密钥验证装饰器
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({'error': '缺少API密钥'}), 401
        
        # 验证API密钥
        user = Users.query.filter_by(api_key=api_key, is_active=True).first()
        if not user:
            return jsonify({'error': 'API密钥无效或已禁用'}), 401
        
        return view_function(*args, **kwargs)
    
    # 重命名装饰器的名称，以便Flask正确处理
    decorated_function.__name__ = view_function.__name__
    return decorated_function

# API状态检查端点
@bp.route('/status')
def api_status():
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'database': 'GenoBase'
    })

# 物种相关API
@bp.route('/species')
@require_api_key
def get_species_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    species_query = Species.query.order_by(Species.scientific_name)
    
    # 过滤条件
    name_filter = request.args.get('name')
    if name_filter:
        species_query = species_query.filter(
            or_(
                Species.scientific_name.contains(name_filter),
                Species.common_name.contains(name_filter)
            )
        )
    
    # 执行分页查询
    species_paginated = species_query.paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化响应
    result = {
        'items': [{
            'species_id': sp.species_id,
            'scientific_name': sp.scientific_name,
            'common_name': sp.common_name,
            'taxonomy_id': sp.taxonomy_id,
            'gene_count': sp.genes.count()
        } for sp in species_paginated.items],
        'total': species_paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': species_paginated.pages
    }
    
    return jsonify(result)

@bp.route('/species/<int:id>')
@require_api_key
def get_species(id):
    species = Species.query.get_or_404(id)
    
    # 获取关联的基因数量
    gene_count = species.genes.count()
    
    # 格式化响应
    result = {
        'species_id': species.species_id,
        'scientific_name': species.scientific_name,
        'common_name': species.common_name,
        'taxonomy_id': species.taxonomy_id,
        'description': species.description,
        'gene_count': gene_count,
        'created_at': species.created_at.isoformat(),
        'updated_at': species.updated_at.isoformat()
    }
    
    # 可选：包含基因列表
    include_genes = request.args.get('include_genes', type=bool)
    if include_genes:
        result['genes'] = [{
            'gene_id': gene.gene_id,
            'gene_name': gene.gene_name,
            'gene_symbol': gene.gene_symbol,
            'chromosome': gene.chromosome
        } for gene in species.genes.all()]
    
    return jsonify(result)

# 基因相关API
@bp.route('/genes')
@require_api_key
def get_genes_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    genes_query = Genes.query
    
    # 过滤条件
    name_filter = request.args.get('name')
    if name_filter:
        genes_query = genes_query.filter(
            or_(
                Genes.gene_name.contains(name_filter),
                Genes.gene_symbol.contains(name_filter)
            )
        )
    
    species_id = request.args.get('species_id', type=int)
    if species_id:
        genes_query = genes_query.filter(Genes.species_id == species_id)
    
    # 排序
    sort_by = request.args.get('sort_by', 'gene_name')
    if sort_by not in ['gene_id', 'gene_name', 'gene_symbol', 'created_at']:
        sort_by = 'gene_name'
    
    sort_order = request.args.get('sort_order', 'asc')
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'
    
    if sort_order == 'asc':
        genes_query = genes_query.order_by(getattr(Genes, sort_by))
    else:
        genes_query = genes_query.order_by(getattr(Genes, sort_by).desc())
    
    # 执行分页查询
    genes_paginated = genes_query.paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化响应
    result = {
        'items': [{
            'gene_id': gene.gene_id,
            'gene_name': gene.gene_name,
            'gene_symbol': gene.gene_symbol,
            'chromosome': gene.chromosome,
            'species_id': gene.species_id,
            'species_name': gene.species.scientific_name if gene.species else None,
            'protein_count': gene.proteins.count(),
            'publication_count': len(gene.publications)
        } for gene in genes_paginated.items],
        'total': genes_paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': genes_paginated.pages
    }
    
    return jsonify(result)

@bp.route('/genes/<int:id>')
@require_api_key
def get_gene(id):
    gene = Genes.query.get_or_404(id)
    
    # 格式化响应
    result = {
        'gene_id': gene.gene_id,
        'gene_name': gene.gene_name,
        'gene_symbol': gene.gene_symbol,
        'chromosome': gene.chromosome,
        'start_position': gene.start_position,
        'end_position': gene.end_position,
        'strand': gene.strand,
        'species_id': gene.species_id,
        'species_name': gene.species.scientific_name if gene.species else None,
        'created_at': gene.created_at.isoformat(),
        'updated_at': gene.updated_at.isoformat()
    }
    
    # 可选：包含序列数据
    include_sequence = request.args.get('include_sequence', type=bool)
    if include_sequence:
        result['sequence'] = gene.sequence
    
    # 可选：包含蛋白质列表
    include_proteins = request.args.get('include_proteins', type=bool)
    if include_proteins:
        result['proteins'] = [{
            'protein_id': protein.protein_id,
            'protein_name': protein.protein_name,
            'uniprot_id': protein.uniprot_id
        } for protein in gene.proteins.all()]
    
    # 可选：包含文献列表
    include_publications = request.args.get('include_publications', type=bool)
    if include_publications:
        result['publications'] = [{
            'publication_id': pub.publication_id,
            'title': pub.title,
            'authors': pub.authors,
            'journal': pub.journal,
            'publication_year': pub.publication_year,
            'doi': pub.doi
        } for pub in gene.publications]
    
    # 可选：包含实验数据列表
    include_experiments = request.args.get('include_experiments', type=bool)
    if include_experiments:
        result['experiments'] = [{
            'experiment_id': exp.experiment_id,
            'experiment_type': exp.experiment_type,
            'conditions': exp.conditions,
            'results': exp.results
        } for exp in gene.experimental_data.all()]
    
    return jsonify(result)

# 蛋白质相关API
@bp.route('/proteins')
@require_api_key
def get_proteins_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    proteins_query = Proteins.query
    
    # 过滤条件
    name_filter = request.args.get('name')
    if name_filter:
        proteins_query = proteins_query.filter(
            or_(
                Proteins.protein_name.contains(name_filter),
                Proteins.uniprot_id.contains(name_filter)
            )
        )
    
    gene_id = request.args.get('gene_id', type=int)
    if gene_id:
        proteins_query = proteins_query.filter(Proteins.gene_id == gene_id)
    
    # 排序
    proteins_query = proteins_query.order_by(Proteins.protein_name)
    
    # 执行分页查询
    proteins_paginated = proteins_query.paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化响应
    result = {
        'items': [{
            'protein_id': protein.protein_id,
            'protein_name': protein.protein_name,
            'uniprot_id': protein.uniprot_id,
            'gene_id': protein.gene_id,
            'gene_name': protein.gene.gene_name if protein.gene else None,
            'sequence_length': len(protein.amino_acid_sequence) if protein.amino_acid_sequence else 0
        } for protein in proteins_paginated.items],
        'total': proteins_paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': proteins_paginated.pages
    }
    
    return jsonify(result)

@bp.route('/proteins/<int:id>')
@require_api_key
def get_protein(id):
    protein = Proteins.query.get_or_404(id)
    
    # 格式化响应
    result = {
        'protein_id': protein.protein_id,
        'protein_name': protein.protein_name,
        'uniprot_id': protein.uniprot_id,
        'gene_id': protein.gene_id,
        'gene_name': protein.gene.gene_name if protein.gene else None,
        'gene_symbol': protein.gene.gene_symbol if protein.gene else None,
        'created_at': protein.created_at.isoformat(),
        'updated_at': protein.updated_at.isoformat()
    }
    
    # 可选：包含序列数据
    include_sequence = request.args.get('include_sequence', type=bool)
    if include_sequence:
        result['amino_acid_sequence'] = protein.amino_acid_sequence
    
    return jsonify(result)

# 文献相关API
@bp.route('/publications')
@require_api_key
def get_publications_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pub_query = Publications.query
    
    # 过滤条件
    title_filter = request.args.get('title')
    if title_filter:
        pub_query = pub_query.filter(Publications.title.contains(title_filter))
    
    author_filter = request.args.get('author')
    if author_filter:
        pub_query = pub_query.filter(Publications.authors.contains(author_filter))
    
    year_filter = request.args.get('year', type=int)
    if year_filter:
        pub_query = pub_query.filter(Publications.publication_year == year_filter)
    
    journal_filter = request.args.get('journal')
    if journal_filter:
        pub_query = pub_query.filter(Publications.journal.contains(journal_filter))
    
    # 排序
    pub_query = pub_query.order_by(Publications.publication_year.desc())
    
    # 执行分页查询
    pub_paginated = pub_query.paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化响应
    result = {
        'items': [{
            'publication_id': pub.publication_id,
            'title': pub.title,
            'authors': pub.authors,
            'journal': pub.journal,
            'publication_year': pub.publication_year,
            'doi': pub.doi,
            'gene_count': len(pub.genes)
        } for pub in pub_paginated.items],
        'total': pub_paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': pub_paginated.pages
    }
    
    return jsonify(result)

@bp.route('/publications/<int:id>')
@require_api_key
def get_publication(id):
    publication = Publications.query.get_or_404(id)
    
    # 格式化响应
    result = {
        'publication_id': publication.publication_id,
        'title': publication.title,
        'authors': publication.authors,
        'journal': publication.journal,
        'publication_year': publication.publication_year,
        'doi': publication.doi,
        'created_at': publication.created_at.isoformat(),
        'updated_at': publication.updated_at.isoformat()
    }
    
    # 可选：包含关联的基因
    include_genes = request.args.get('include_genes', type=bool)
    if include_genes:
        result['genes'] = [{
            'gene_id': gene.gene_id,
            'gene_name': gene.gene_name,
            'gene_symbol': gene.gene_symbol,
            'species_name': gene.species.scientific_name if gene.species else None
        } for gene in publication.genes]
    
    # 可选：包含实验数据
    include_experiments = request.args.get('include_experiments', type=bool)
    if include_experiments:
        result['experiments'] = [{
            'experiment_id': exp.experiment_id,
            'experiment_type': exp.experiment_type,
            'conditions': exp.conditions,
            'results': exp.results
        } for exp in publication.experimental_data.all()]
    
    return jsonify(result)

# 实验数据相关API
@bp.route('/experiments')
@require_api_key
def get_experiments_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    exp_query = Experimental_Data.query
    
    # 过滤条件
    type_filter = request.args.get('type')
    if type_filter:
        exp_query = exp_query.filter(Experimental_Data.experiment_type.contains(type_filter))
    
    gene_id = request.args.get('gene_id', type=int)
    if gene_id:
        exp_query = exp_query.filter(Experimental_Data.gene_id == gene_id)
    
    publication_id = request.args.get('publication_id', type=int)
    if publication_id:
        exp_query = exp_query.filter(Experimental_Data.publication_id == publication_id)
    
    # 排序
    exp_query = exp_query.order_by(Experimental_Data.created_at.desc())
    
    # 执行分页查询
    exp_paginated = exp_query.paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化响应
    result = {
        'items': [{
            'experiment_id': exp.experiment_id,
            'experiment_type': exp.experiment_type,
            'gene_id': exp.gene_id,
            'gene_name': exp.gene.gene_name if exp.gene else None,
            'publication_id': exp.publication_id,
            'publication_title': exp.publication.title if exp.publication else None
        } for exp in exp_paginated.items],
        'total': exp_paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': exp_paginated.pages
    }
    
    return jsonify(result)

@bp.route('/experiments/<int:id>')
@require_api_key
def get_experiment(id):
    experiment = Experimental_Data.query.get_or_404(id)
    
    # 格式化响应
    result = {
        'experiment_id': experiment.experiment_id,
        'experiment_type': experiment.experiment_type,
        'conditions': experiment.conditions,
        'results': experiment.results,
        'gene_id': experiment.gene_id,
        'gene_name': experiment.gene.gene_name if experiment.gene else None,
        'gene_symbol': experiment.gene.gene_symbol if experiment.gene else None,
        'publication_id': experiment.publication_id,
        'publication_title': experiment.publication.title if experiment.publication else None,
        'created_at': experiment.created_at.isoformat(),
        'updated_at': experiment.updated_at.isoformat()
    }
    
    return jsonify(result)

# 高级搜索API
@bp.route('/search')
@require_api_key
def search_api():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '搜索词为空'}), 400
    
    category = request.args.get('category', 'all')
    results = []
    
    if category == 'gene' or category == 'all':
        genes = Genes.query.filter(
            or_(
                Genes.gene_name.contains(query),
                Genes.gene_symbol.contains(query)
            )
        ).all()
        results.extend([{
            'type': 'gene',
            'id': gene.gene_id,
            'name': gene.gene_name,
            'symbol': gene.gene_symbol,
            'species': gene.species.scientific_name if gene.species else None
        } for gene in genes])
    
    if category == 'protein' or category == 'all':
        proteins = Proteins.query.filter(
            or_(
                Proteins.protein_name.contains(query),
                Proteins.uniprot_id.contains(query)
            )
        ).all()
        results.extend([{
            'type': 'protein',
            'id': protein.protein_id,
            'name': protein.protein_name,
            'uniprot_id': protein.uniprot_id,
            'gene': protein.gene.gene_name if protein.gene else None
        } for protein in proteins])
    
    if category == 'species' or category == 'all':
        species = Species.query.filter(
            or_(
                Species.scientific_name.contains(query),
                Species.common_name.contains(query),
                Species.taxonomy_id.contains(query)
            )
        ).all()
        results.extend([{
            'type': 'species',
            'id': sp.species_id,
            'scientific_name': sp.scientific_name,
            'common_name': sp.common_name,
            'taxonomy_id': sp.taxonomy_id
        } for sp in species])
    
    if category == 'publication' or category == 'all':
        publications = Publications.query.filter(
            or_(
                Publications.title.contains(query),
                Publications.authors.contains(query),
                Publications.journal.contains(query),
                Publications.doi.contains(query)
            )
        ).all()
        results.extend([{
            'type': 'publication',
            'id': pub.publication_id,
            'title': pub.title,
            'authors': pub.authors,
            'journal': pub.journal,
            'year': pub.publication_year
        } for pub in publications])
    
    return jsonify({
        'query': query,
        'category': category,
        'total': len(results),
        'results': results
    }) 