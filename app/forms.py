from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FileField, SelectMultipleField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import Users, Genes, Publications

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('用户类型', choices=[('reader', '读者'), ('creator', '创建者'), ('manager', '管理员')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被使用，请更换一个。')
    
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('此邮箱已注册，请更换一个。')

class CreatorProfileForm(FlaskForm):
    institution = StringField('所属机构', validators=[DataRequired()])
    research_field = StringField('研究领域', validators=[DataRequired()])
    submit = SubmitField('保存')

class ManagerProfileForm(FlaskForm):
    department = StringField('部门', validators=[DataRequired()])
    access_level = SelectField('访问级别', choices=[('limited', '有限访问'), ('full', '完全访问')])
    submit = SubmitField('保存')

class ReaderProfileForm(FlaskForm):
    organization = StringField('组织', validators=[Optional()])
    subscription_type = SelectField('订阅类型', choices=[('free', '免费版'), ('premium', '高级版')])
    submit = SubmitField('保存')

class SearchForm(FlaskForm):
    query = StringField('搜索', validators=[DataRequired()])
    category = SelectField('类别', choices=[
        ('all', '全部'), 
        ('gene', '基因'), 
        ('protein', '蛋白质'), 
        ('species', '物种'), 
        ('publication', '文献')
    ])
    submit = SubmitField('搜索')

class SpeciesForm(FlaskForm):
    scientific_name = StringField('学名', validators=[DataRequired()])
    common_name = StringField('常用名')
    taxonomy_id = StringField('分类ID')
    description = TextAreaField('描述')
    submit = SubmitField('提交')

class GeneForm(FlaskForm):
    gene_name = StringField('基因名称', validators=[DataRequired()])
    gene_symbol = StringField('基因符号')
    sequence = TextAreaField('序列', validators=[DataRequired()])
    chromosome = StringField('染色体')
    start_position = IntegerField('起始位置', validators=[Optional()])
    end_position = IntegerField('终止位置', validators=[Optional()])
    strand = SelectField('链', choices=[('+', '+'), ('-', '-')])
    species_id = SelectField('物种', coerce=int)
    submit = SubmitField('提交')

class ProteinForm(FlaskForm):
    protein_name = StringField('蛋白质名称', validators=[DataRequired()])
    uniprot_id = StringField('UniProt ID', validators=[DataRequired()])
    gene_id = IntegerField('基因ID', validators=[DataRequired()])
    amino_acid_sequence = TextAreaField('氨基酸序列', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_gene_id(self, field):
        # 验证选择的基因是否存在
        gene = Genes.query.get(field.data)
        if not gene:
            raise ValidationError('所输入基因不存在，请重新选择')

class PublicationForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    authors = TextAreaField('作者', validators=[DataRequired()])
    journal = StringField('期刊')
    publication_year = IntegerField('发表年份', validators=[Optional()])
    doi = StringField('DOI')
    gene_ids = SelectMultipleField('关联基因', coerce=int)
    submit = SubmitField('提交')

class ExperimentalDataForm(FlaskForm):
    experiment_type = StringField('实验类型', validators=[DataRequired()])
    conditions = TextAreaField('实验条件', validators=[DataRequired()])
    results = TextAreaField('实验结果', validators=[DataRequired()])
    gene_id = IntegerField('关联基因', validators=[Optional()])
    publication_id = SelectField('关联文献', coerce=int)
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(ExperimentalDataForm, self).__init__(*args, **kwargs)
        self.gene_id.choices = [(g.gene_id, f"{g.gene_name} ({g.gene_symbol})") 
                               for g in Genes.query.order_by(Genes.gene_name).all()]
        self.publication_id.choices = [(0, '-- 选择文献 --')] + [
            (p.publication_id, f"{p.title} ({p.publication_year})") 
            for p in Publications.query.order_by(Publications.publication_year.desc()).all()
        ]

class SequenceUploadForm(FlaskForm):
    file = FileField('序列文件 (FASTA格式)', validators=[DataRequired()])
    sequence_type = SelectField('序列类型', choices=[('gene', '基因'), ('protein', '蛋白质')])
    species_id = SelectField('物种', coerce=int)
    submit = SubmitField('上传') 

