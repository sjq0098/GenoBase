# GenoBase API 文档

## 1. 概述

GenoBase API 提供了一套完整的 RESTful 接口，用于访问和管理生物信息数据。API 支持 JSON 格式的请求和响应，并使用 JWT 进行身份验证。

### 1.1 基础 URL

```
https://api.genobase.com/v1
```

### 1.2 认证方式

所有 API 请求都需要在 HTTP 头部包含 JWT 令牌：

```
Authorization: Bearer <token>
```

对于需要 API key 的请求，需要在 HTTP 头部包含 API key：

```
X-API-Key: <api_key>
```

### 1.3 响应格式

所有 API 响应都使用 JSON 格式，包含以下字段：

```json
{
  "code": 200,
  "message": "Success",
  "data": {}
}
```

### 1.4 错误处理

当发生错误时，API 将返回相应的 HTTP 状态码和错误信息：

```json
{
  "code": 400,
  "message": "Bad Request",
  "errors": [
    {
      "field": "username",
      "message": "Username is required"
    }
  ]
}
```

## 2. 认证 API

### 2.1 用户注册

**请求**：`POST /auth/register`

**描述**：注册新用户

**请求体**：

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "reader"
}
```

**响应**：

```json
{
  "code": 201,
  "message": "User created successfully",
  "data": {
    "user_id": 1,
    "username": "string",
    "email": "string",
    "role": "reader",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### 2.2 用户登录

**请求**：`POST /auth/login`

**描述**：用户登录并获取 JWT 令牌

**请求体**：

```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "user_id": 1,
      "username": "string",
      "email": "string",
      "role": "reader"
    }
  }
}
```

### 2.3 获取 API Key

**请求**：`POST /auth/api-key`

**描述**：为当前用户生成 API key

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "API key generated successfully",
  "data": {
    "api_key": "string",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

## 3. 用户 API

### 3.1 获取当前用户信息

**请求**：`GET /users/me`

**描述**：获取当前登录用户的信息

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "user_id": 1,
    "username": "string",
    "email": "string",
    "role": "reader",
    "api_key": "string",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 3.2 更新用户信息

**请求**：`PUT /users/me`

**描述**：更新当前用户的信息

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "email": "string",
  "password": "string"
}
```

**响应**：

```json
{
  "code": 200,
  "message": "User updated successfully",
  "data": {
    "user_id": 1,
    "username": "string",
    "email": "string",
    "role": "reader",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

## 4. 物种 API

### 4.1 获取物种列表

**请求**：`GET /species`

**描述**：获取物种列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `search`：搜索关键词

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "species_id": 1,
        "scientific_name": "string",
        "common_name": "string",
        "taxonomy_id": "string",
        "description": "string",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 4.2 获取物种详情

**请求**：`GET /species/{species_id}`

**描述**：获取指定物种的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "species_id": 1,
    "scientific_name": "string",
    "common_name": "string",
    "taxonomy_id": "string",
    "description": "string",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 4.3 创建物种

**请求**：`POST /species`

**描述**：创建新物种（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "scientific_name": "string",
  "common_name": "string",
  "taxonomy_id": "string",
  "description": "string"
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Species created successfully",
  "data": {
    "species_id": 1,
    "scientific_name": "string",
    "common_name": "string",
    "taxonomy_id": "string",
    "description": "string",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 4.4 更新物种

**请求**：`PUT /species/{species_id}`

**描述**：更新指定物种的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "scientific_name": "string",
  "common_name": "string",
  "taxonomy_id": "string",
  "description": "string"
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Species updated successfully",
  "data": {
    "species_id": 1,
    "scientific_name": "string",
    "common_name": "string",
    "taxonomy_id": "string",
    "description": "string",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 4.5 删除物种

**请求**：`DELETE /species/{species_id}`

**描述**：删除指定物种（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Species deleted successfully",
  "data": null
}
```

## 5. 基因 API

### 5.1 获取基因列表

**请求**：`GET /genes`

**描述**：获取基因列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `search`：搜索关键词
- `species_id`：物种 ID 过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "gene_id": 1,
        "gene_name": "string",
        "gene_symbol": "string",
        "sequence": "string",
        "chromosome": "string",
        "start_position": 1000,
        "end_position": 2000,
        "strand": "+",
        "species_id": 1,
        "species": {
          "species_id": 1,
          "scientific_name": "string"
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 5.2 获取基因详情

**请求**：`GET /genes/{gene_id}`

**描述**：获取指定基因的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "gene_id": 1,
    "gene_name": "string",
    "gene_symbol": "string",
    "sequence": "string",
    "chromosome": "string",
    "start_position": 1000,
    "end_position": 2000,
    "strand": "+",
    "species_id": 1,
    "species": {
      "species_id": 1,
      "scientific_name": "string",
      "common_name": "string"
    },
    "transcripts": [
      {
        "transcript_id": 1,
        "transcript_name": "string",
        "transcript_type": "string",
        "sequence": "string"
      }
    ],
    "proteins": [
      {
        "protein_id": 1,
        "protein_name": "string",
        "uniprot_id": "string",
        "amino_acid_sequence": "string"
      }
    ],
    "publications": [
      {
        "publication_id": 1,
        "title": "string",
        "authors": "string",
        "journal": "string",
        "publication_year": 2023,
        "doi": "string"
      }
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 5.3 创建基因

**请求**：`POST /genes`

**描述**：创建新基因（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "gene_name": "string",
  "gene_symbol": "string",
  "sequence": "string",
  "chromosome": "string",
  "start_position": 1000,
  "end_position": 2000,
  "strand": "+",
  "species_id": 1
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Gene created successfully",
  "data": {
    "gene_id": 1,
    "gene_name": "string",
    "gene_symbol": "string",
    "sequence": "string",
    "chromosome": "string",
    "start_position": 1000,
    "end_position": 2000,
    "strand": "+",
    "species_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 5.4 更新基因

**请求**：`PUT /genes/{gene_id}`

**描述**：更新指定基因的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "gene_name": "string",
  "gene_symbol": "string",
  "sequence": "string",
  "chromosome": "string",
  "start_position": 1000,
  "end_position": 2000,
  "strand": "+",
  "species_id": 1
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Gene updated successfully",
  "data": {
    "gene_id": 1,
    "gene_name": "string",
    "gene_symbol": "string",
    "sequence": "string",
    "chromosome": "string",
    "start_position": 1000,
    "end_position": 2000,
    "strand": "+",
    "species_id": 1,
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 5.5 删除基因

**请求**：`DELETE /genes/{gene_id}`

**描述**：删除指定基因（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Gene deleted successfully",
  "data": null
}
```

## 6. 转录本 API

### 6.1 获取转录本列表

**请求**：`GET /transcripts`

**描述**：获取转录本列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `search`：搜索关键词
- `gene_id`：基因 ID 过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "transcript_id": 1,
        "transcript_name": "string",
        "transcript_type": "string",
        "sequence": "string",
        "gene_id": 1,
        "gene": {
          "gene_id": 1,
          "gene_name": "string",
          "gene_symbol": "string"
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 6.2 获取转录本详情

**请求**：`GET /transcripts/{transcript_id}`

**描述**：获取指定转录本的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "transcript_id": 1,
    "transcript_name": "string",
    "transcript_type": "string",
    "sequence": "string",
    "gene_id": 1,
    "gene": {
      "gene_id": 1,
      "gene_name": "string",
      "gene_symbol": "string",
      "species": {
        "species_id": 1,
        "scientific_name": "string"
      }
    },
    "expression_data": [
      {
        "expression_id": 1,
        "tissue": "string",
        "condition": "string",
        "expression_level": 1.5,
        "measurement_unit": "string"
      }
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 6.3 创建转录本

**请求**：`POST /transcripts`

**描述**：创建新转录本（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "transcript_name": "string",
  "transcript_type": "string",
  "sequence": "string",
  "gene_id": 1
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Transcript created successfully",
  "data": {
    "transcript_id": 1,
    "transcript_name": "string",
    "transcript_type": "string",
    "sequence": "string",
    "gene_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 6.4 更新转录本

**请求**：`PUT /transcripts/{transcript_id}`

**描述**：更新指定转录本的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "transcript_name": "string",
  "transcript_type": "string",
  "sequence": "string",
  "gene_id": 1
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Transcript updated successfully",
  "data": {
    "transcript_id": 1,
    "transcript_name": "string",
    "transcript_type": "string",
    "sequence": "string",
    "gene_id": 1,
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 6.5 删除转录本

**请求**：`DELETE /transcripts/{transcript_id}`

**描述**：删除指定转录本（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Transcript deleted successfully",
  "data": null
}
```

## 7. 蛋白质 API

### 7.1 获取蛋白质列表

**请求**：`GET /proteins`

**描述**：获取蛋白质列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `search`：搜索关键词
- `gene_id`：基因 ID 过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "protein_id": 1,
        "protein_name": "string",
        "uniprot_id": "string",
        "amino_acid_sequence": "string",
        "gene_id": 1,
        "gene": {
          "gene_id": 1,
          "gene_name": "string",
          "gene_symbol": "string"
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 7.2 获取蛋白质详情

**请求**：`GET /proteins/{protein_id}`

**描述**：获取指定蛋白质的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "protein_id": 1,
    "protein_name": "string",
    "uniprot_id": "string",
    "amino_acid_sequence": "string",
    "gene_id": 1,
    "gene": {
      "gene_id": 1,
      "gene_name": "string",
      "gene_symbol": "string",
      "species": {
        "species_id": 1,
        "scientific_name": "string"
      }
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 7.3 创建蛋白质

**请求**：`POST /proteins`

**描述**：创建新蛋白质（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "protein_name": "string",
  "uniprot_id": "string",
  "amino_acid_sequence": "string",
  "gene_id": 1
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Protein created successfully",
  "data": {
    "protein_id": 1,
    "protein_name": "string",
    "uniprot_id": "string",
    "amino_acid_sequence": "string",
    "gene_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 7.4 更新蛋白质

**请求**：`PUT /proteins/{protein_id}`

**描述**：更新指定蛋白质的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "protein_name": "string",
  "uniprot_id": "string",
  "amino_acid_sequence": "string",
  "gene_id": 1
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Protein updated successfully",
  "data": {
    "protein_id": 1,
    "protein_name": "string",
    "uniprot_id": "string",
    "amino_acid_sequence": "string",
    "gene_id": 1,
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 7.5 删除蛋白质

**请求**：`DELETE /proteins/{protein_id}`

**描述**：删除指定蛋白质（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Protein deleted successfully",
  "data": null
}
```

## 8. 表达数据 API

### 8.1 获取表达数据列表

**请求**：`GET /expression`

**描述**：获取表达数据列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `gene_id`：基因 ID 过滤
- `transcript_id`：转录本 ID 过滤
- `tissue`：组织过滤
- `condition`：条件过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "expression_id": 1,
        "gene_id": 1,
        "transcript_id": 1,
        "tissue": "string",
        "condition": "string",
        "expression_level": 1.5,
        "measurement_unit": "string",
        "gene": {
          "gene_id": 1,
          "gene_name": "string",
          "gene_symbol": "string"
        },
        "transcript": {
          "transcript_id": 1,
          "transcript_name": "string"
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 8.2 获取表达数据详情

**请求**：`GET /expression/{expression_id}`

**描述**：获取指定表达数据的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "expression_id": 1,
    "gene_id": 1,
    "transcript_id": 1,
    "tissue": "string",
    "condition": "string",
    "expression_level": 1.5,
    "measurement_unit": "string",
    "gene": {
      "gene_id": 1,
      "gene_name": "string",
      "gene_symbol": "string",
      "species": {
        "species_id": 1,
        "scientific_name": "string"
      }
    },
    "transcript": {
      "transcript_id": 1,
      "transcript_name": "string",
      "transcript_type": "string"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 8.3 创建表达数据

**请求**：`POST /expression`

**描述**：创建新表达数据（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "gene_id": 1,
  "transcript_id": 1,
  "tissue": "string",
  "condition": "string",
  "expression_level": 1.5,
  "measurement_unit": "string"
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Expression data created successfully",
  "data": {
    "expression_id": 1,
    "gene_id": 1,
    "transcript_id": 1,
    "tissue": "string",
    "condition": "string",
    "expression_level": 1.5,
    "measurement_unit": "string",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 8.4 更新表达数据

**请求**：`PUT /expression/{expression_id}`

**描述**：更新指定表达数据的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "gene_id": 1,
  "transcript_id": 1,
  "tissue": "string",
  "condition": "string",
  "expression_level": 1.5,
  "measurement_unit": "string"
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Expression data updated successfully",
  "data": {
    "expression_id": 1,
    "gene_id": 1,
    "transcript_id": 1,
    "tissue": "string",
    "condition": "string",
    "expression_level": 1.5,
    "measurement_unit": "string",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 8.5 删除表达数据

**请求**：`DELETE /expression/{expression_id}`

**描述**：删除指定表达数据（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Expression data deleted successfully",
  "data": null
}
```

## 9. 文献 API

### 9.1 获取文献列表

**请求**：`GET /publications`

**描述**：获取文献列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `search`：搜索关键词
- `year`：发表年份过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "publication_id": 1,
        "title": "string",
        "authors": "string",
        "journal": "string",
        "publication_year": 2023,
        "doi": "string",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 9.2 获取文献详情

**请求**：`GET /publications/{publication_id}`

**描述**：获取指定文献的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "publication_id": 1,
    "title": "string",
    "authors": "string",
    "journal": "string",
    "publication_year": 2023,
    "doi": "string",
    "genes": [
      {
        "gene_id": 1,
        "gene_name": "string",
        "gene_symbol": "string",
        "species": {
          "species_id": 1,
          "scientific_name": "string"
        }
      }
    ],
    "experimental_data": [
      {
        "experiment_id": 1,
        "experiment_type": "string",
        "conditions": "string",
        "results": "string"
      }
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 9.3 创建文献

**请求**：`POST /publications`

**描述**：创建新文献（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "title": "string",
  "authors": "string",
  "journal": "string",
  "publication_year": 2023,
  "doi": "string"
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Publication created successfully",
  "data": {
    "publication_id": 1,
    "title": "string",
    "authors": "string",
    "journal": "string",
    "publication_year": 2023,
    "doi": "string",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 9.4 更新文献

**请求**：`PUT /publications/{publication_id}`

**描述**：更新指定文献的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "title": "string",
  "authors": "string",
  "journal": "string",
  "publication_year": 2023,
  "doi": "string"
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Publication updated successfully",
  "data": {
    "publication_id": 1,
    "title": "string",
    "authors": "string",
    "journal": "string",
    "publication_year": 2023,
    "doi": "string",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 9.5 删除文献

**请求**：`DELETE /publications/{publication_id}`

**描述**：删除指定文献（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Publication deleted successfully",
  "data": null
}
```

## 10. 实验数据 API

### 10.1 获取实验数据列表

**请求**：`GET /experimental`

**描述**：获取实验数据列表，支持分页和搜索

**参数**：
- `skip`：跳过的记录数（默认：0）
- `limit`：返回的记录数（默认：10）
- `gene_id`：基因 ID 过滤
- `publication_id`：文献 ID 过滤
- `experiment_type`：实验类型过滤

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "experiment_id": 1,
        "experiment_type": "string",
        "conditions": "string",
        "results": "string",
        "gene_id": 1,
        "publication_id": 1,
        "gene": {
          "gene_id": 1,
          "gene_name": "string",
          "gene_symbol": "string"
        },
        "publication": {
          "publication_id": 1,
          "title": "string",
          "authors": "string"
        },
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 10
  }
}
```

### 10.2 获取实验数据详情

**请求**：`GET /experimental/{experiment_id}`

**描述**：获取指定实验数据的详细信息

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "experiment_id": 1,
    "experiment_type": "string",
    "conditions": "string",
    "results": "string",
    "gene_id": 1,
    "publication_id": 1,
    "gene": {
      "gene_id": 1,
      "gene_name": "string",
      "gene_symbol": "string",
      "species": {
        "species_id": 1,
        "scientific_name": "string"
      }
    },
    "publication": {
      "publication_id": 1,
      "title": "string",
      "authors": "string",
      "journal": "string",
      "publication_year": 2023,
      "doi": "string"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 10.3 创建实验数据

**请求**：`POST /experimental`

**描述**：创建新实验数据（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "experiment_type": "string",
  "conditions": "string",
  "results": "string",
  "gene_id": 1,
  "publication_id": 1
}
```

**响应**：

```json
{
  "code": 201,
  "message": "Experimental data created successfully",
  "data": {
    "experiment_id": 1,
    "experiment_type": "string",
    "conditions": "string",
    "results": "string",
    "gene_id": 1,
    "publication_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 10.4 更新实验数据

**请求**：`PUT /experimental/{experiment_id}`

**描述**：更新指定实验数据的信息（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "experiment_type": "string",
  "conditions": "string",
  "results": "string",
  "gene_id": 1,
  "publication_id": 1
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Experimental data updated successfully",
  "data": {
    "experiment_id": 1,
    "experiment_type": "string",
    "conditions": "string",
    "results": "string",
    "gene_id": 1,
    "publication_id": 1,
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

### 10.5 删除实验数据

**请求**：`DELETE /experimental/{experiment_id}`

**描述**：删除指定实验数据（需要创建者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Experimental data deleted successfully",
  "data": null
}
```

## 11. 数据导入导出 API

### 11.1 批量导入数据

**请求**：`POST /import`

**描述**：批量导入数据（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**请求体**：multipart/form-data
- `file`：数据文件（CSV、TSV、Excel）
- `data_type`：数据类型（species、gene、transcript、protein、expression、publication、experimental）
- `options`：导入选项（JSON 字符串）

**响应**：

```json
{
  "code": 200,
  "message": "Data import started",
  "data": {
    "import_id": "string",
    "status": "processing",
    "total_records": 100,
    "processed_records": 0,
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### 11.2 获取导入状态

**请求**：`GET /import/{import_id}`

**描述**：获取数据导入的状态（需要创建者或管理者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "import_id": "string",
    "status": "completed",
    "total_records": 100,
    "processed_records": 100,
    "successful_records": 95,
    "failed_records": 5,
    "errors": [
      {
        "row": 10,
        "message": "Invalid data format"
      }
    ],
    "created_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z"
  }
}
```

### 11.3 导出数据

**请求**：`POST /export`

**描述**：导出数据（需要创建者、管理者或阅读者权限）

**请求头**：需要 JWT 认证

**请求体**：

```json
{
  "data_type": "gene",
  "format": "csv",
  "filters": {
    "species_id": 1,
    "chromosome": "1"
  },
  "fields": ["gene_id", "gene_name", "gene_symbol", "sequence", "chromosome"]
}
```

**响应**：

```json
{
  "code": 200,
  "message": "Data export started",
  "data": {
    "export_id": "string",
    "status": "processing",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### 11.4 获取导出状态

**请求**：`GET /export/{export_id}`

**描述**：获取数据导出的状态（需要创建者、管理者或阅读者权限）

**请求头**：需要 JWT 认证

**响应**：

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "export_id": "string",
    "status": "completed",
    "download_url": "https://api.genobase.com/v1/download/export/string",
    "expires_at": "2023-01-02T00:00:00Z",
    "created_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z"
  }
}
```

### 11.5 下载导出文件

**请求**：`GET /download/export/{export_id}`

**描述**：下载导出的数据文件（需要创建者、管理者或阅读者权限）

**请求头**：需要 JWT 认证

**响应**：文件下载 