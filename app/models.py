from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_type = db.Column(db.Enum('creator', 'manager', 'reader'), nullable=False)
    api_key = db.Column(db.String(64), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    creator = db.relationship('Creators', backref='user', uselist=False, cascade="all, delete-orphan")
    manager = db.relationship('Managers', backref='user', uselist=False, cascade="all, delete-orphan")
    reader = db.relationship('Readers', backref='user', uselist=False, cascade="all, delete-orphan")
    
    def __init__(self, username, email, user_type):
        self.username = username
        self.email = email
        self.user_type = user_type
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_creator(self):
        return self.user_type == 'creator'
    
    def is_manager(self):
        return self.user_type == 'manager'
    
    def is_reader(self):
        return self.user_type == 'reader'

    def get_user_type_display(self):
        type_map = {
            'creator': '创建者',
            'manager': '管理员',
            'reader': '读者'
        }
        return type_map.get(self.user_type, self.user_type)

class Creators(db.Model):
    __tablename__ = 'Creators'
    
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), primary_key=True)
    institution = db.Column(db.String(100))
    research_field = db.Column(db.String(100))
    max_storage_size = db.Column(db.BigInteger, default=1073741824)  # 默认1GB

class Managers(db.Model):
    __tablename__ = 'Managers'
    
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), primary_key=True)
    department = db.Column(db.String(100))
    access_level = db.Column(db.Enum('full', 'limited'), nullable=False)

class Readers(db.Model):
    __tablename__ = 'Readers'
    
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), primary_key=True)
    organization = db.Column(db.String(100))
    subscription_type = db.Column(db.Enum('free', 'premium'), nullable=False)

class Species(db.Model):
    __tablename__ = 'Species'
    
    species_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scientific_name = db.Column(db.String(100), nullable=False)
    common_name = db.Column(db.String(100))
    taxonomy_id = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    genes = db.relationship('Genes', backref='species', lazy='dynamic')

class Genes(db.Model):
    __tablename__ = 'Genes'
    
    gene_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gene_name = db.Column(db.String(100), nullable=False)
    gene_symbol = db.Column(db.String(50))
    sequence = db.Column(db.Text, nullable=False)
    chromosome = db.Column(db.String(50))
    start_position = db.Column(db.Integer)
    end_position = db.Column(db.Integer)
    strand = db.Column(db.Enum('+', '-'))
    species_id = db.Column(db.Integer, db.ForeignKey('Species.species_id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    proteins = db.relationship('Proteins', backref='gene', lazy='dynamic')
    publications = db.relationship('Publications', secondary='Gene_Publications', backref=db.backref('genes', lazy='dynamic'))
    experimental_data = db.relationship('Experimental_Data', backref='gene', lazy='dynamic')

class Proteins(db.Model):
    __tablename__ = 'Proteins'
    
    protein_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    protein_name = db.Column(db.String(100), nullable=False)
    uniprot_id = db.Column(db.String(50))
    amino_acid_sequence = db.Column(db.Text, nullable=False)
    gene_id = db.Column(db.Integer, db.ForeignKey('Genes.gene_id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class Publications(db.Model):
    __tablename__ = 'Publications'
    
    publication_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.Text, nullable=False)
    journal = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    doi = db.Column(db.String(100))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    experimental_data = db.relationship('Experimental_Data', backref='publication', lazy='dynamic')

class Gene_Publications(db.Model):
    __tablename__ = 'Gene_Publications'
    
    gene_id = db.Column(db.Integer, db.ForeignKey('Genes.gene_id'), primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('Publications.publication_id'), primary_key=True)

class Experimental_Data(db.Model):
    __tablename__ = 'Experimental_Data'
    
    experiment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_type = db.Column(db.String(100), nullable=False)
    conditions = db.Column(db.Text)
    results = db.Column(db.Text)
    gene_id = db.Column(db.Integer, db.ForeignKey('Genes.gene_id'))
    publication_id = db.Column(db.Integer, db.ForeignKey('Publications.publication_id'))
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserRoleInfo(db.Model):
    __tablename__ = 'UserRoleInfo'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120))
    user_type = db.Column(db.String(20))
    affiliation = db.Column(db.String(128))
    role_detail = db.Column(db.String(128))
    is_active = db.Column(db.Boolean)

class GeneProteinCountBySpecies(db.Model):
    __tablename__ = 'GeneProteinCountBySpecies'
    __table_args__ = {'extend_existing': True}
    gene_id = db.Column(db.Integer, primary_key=True)
    gene_name = db.Column(db.String(100))
    species_name = db.Column(db.String(100))
    protein_count = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id)) 