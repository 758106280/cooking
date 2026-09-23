# 数据模型设计

## 1. 设计原则

- 菜谱、食材和制作步骤拆分存储，便于搜索和人数换算。
- 餐次、分类和标签使用独立字段或关联表，避免将筛选条件写死在前端。
- 图片只在数据库保存相对路径，文件本身保存在本地 `data/uploads/`。
- 第一版使用 SQLite，通过 SQLAlchemy 和 Alembic 保留后续迁移 PostgreSQL 的空间。

## 2. 实体关系

```text
users
  ├── favorites ── recipes
  └── user_preferences

recipes
  ├── recipe_ingredients ── ingredients
  ├── recipe_steps
  ├── categories
  └── recipe_tags ── tags
```

## 3. 表定义

### users

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| username | varchar(64) | 登录名，唯一 |
| password_hash | varchar(255) | 密码哈希 |
| role | varchar(32) | 第一版固定为 `admin` |
| is_active | boolean | 是否启用 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### recipes

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| name | varchar(128) | 菜谱名称 |
| description | text | 菜谱简介 |
| cover_image | varchar(255) | 封面相对路径 |
| meal_type | varchar(32) | `breakfast`、`lunch`、`dinner` |
| category_id | integer | 分类 ID |
| difficulty | varchar(32) | `easy`、`medium`、`hard` |
| cooking_time | integer | 烹饪时间，单位分钟 |
| servings | integer | 默认份数 |
| status | varchar(32) | `draft`、`published`、`archived` |
| tips | text | 烹饪技巧 |
| nutrition | text | JSON 格式的可选营养信息 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### ingredients

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| name | varchar(128) | 食材名称 |
| category | varchar(64) | 食材分类 |
| created_at | datetime | 创建时间 |

### recipe_ingredients

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| recipe_id | integer | 菜谱 ID |
| ingredient_id | integer | 食材 ID |
| amount | decimal | 用量数值 |
| unit | varchar(32) | 克、个、勺等 |
| note | varchar(255) | 备注，例如“切片” |
| sort_order | integer | 展示顺序 |

### recipe_steps

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| recipe_id | integer | 菜谱 ID |
| step_no | integer | 步骤序号 |
| description | text | 步骤说明 |
| duration_seconds | integer | 可选计时，单位秒 |
| image | varchar(255) | 可选步骤图片 |

### categories

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| name | varchar(64) | 分类名称 |
| type | varchar(32) | `meal`、`cuisine`、`ingredient` |
| sort_order | integer | 排序 |
| is_active | boolean | 是否启用 |

### tags

| 字段 | 类型 | 说明 |
|---|---|---|
| id | integer | 主键 |
| name | varchar(64) | 标签名称 |
| type | varchar(32) | 标签类型 |

### recipe_tags

| 字段 | 类型 | 说明 |
|---|---|---|
| recipe_id | integer | 菜谱 ID |
| tag_id | integer | 标签 ID |

主键为 `(recipe_id, tag_id)`。

### favorites

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | integer | 用户 ID |
| recipe_id | integer | 菜谱 ID |
| created_at | datetime | 收藏时间 |

主键为 `(user_id, recipe_id)`。

### user_preferences

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | integer | 用户 ID |
| preferred_cuisines | text | JSON 数组 |
| disliked_ingredients | text | JSON 数组 |
| allergies | text | JSON 数组 |
| cooking_level | varchar(32) | 烹饪水平 |
| appliances | text | JSON 数组 |
| default_servings | integer | 默认人数 |

## 4. 第一版初始化数据

- 早餐、午餐、晚餐三个餐次。
- 简单、中等、困难三个难度。
- 当前内置 29 道早餐、38 道午餐、41 道晚餐菜谱。
- 中餐覆盖鲁、川、粤、苏、浙、闽、湘、徽八大菜系，另含西餐和烘焙分类。
- 初始化一个管理员账号。
