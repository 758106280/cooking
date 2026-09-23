# API 接口约定

## 1. 基础信息

- 基础地址：`/api`
- 数据格式：JSON
- 字段命名：`snake_case`
- 时间格式：ISO 8601
- 认证方式：HttpOnly Cookie

## 2. 通用响应

成功响应：

```json
{
  "data": {},
  "message": "success"
}
```

列表响应：

```json
{
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  },
  "message": "success"
}
```

错误响应：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不正确",
    "details": {}
  }
}
```

## 3. 系统接口

### GET `/api/health`

检查后端服务状态。

响应：

```json
{
  "status": "ok",
  "service": "cooking-api"
}
```

## 4. 公共菜谱接口

### GET `/api/recipes`

获取已发布菜谱列表。

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| keyword | string | 菜名或食材关键词 |
| meal_type | string | `breakfast`、`lunch`、`dinner` |
| difficulty | string | `easy`、`medium`、`hard` |
| max_cooking_time | integer | 最大烹饪时间 |
| category_id | integer | 分类 ID |
| tag_id | integer | 标签 ID |
| page | integer | 页码，默认 1 |
| page_size | integer | 每页数量，默认 20 |

### GET `/api/recipes/{recipe_id}`

获取菜谱详情，包括：

- 基本信息
- 食材清单
- 制作步骤
- 标签
- 同餐次推荐菜谱

### GET `/api/categories`

获取分类列表。

### GET `/api/tags`

获取标签列表。

## 5. 收藏接口

以下接口需要登录。

### GET `/api/favorites`

获取当前用户收藏的菜谱。

### GET `/api/favorites/{recipe_id}/status`

获取指定菜谱的收藏状态。

### POST `/api/favorites/{recipe_id}`

收藏指定菜谱。

### DELETE `/api/favorites/{recipe_id}`

取消收藏指定菜谱。

## 6. 用户偏好接口

### GET `/api/preferences`

获取当前用户的饮食偏好。

### PATCH `/api/preferences`

更新喜欢的菜系、忌口、过敏食材、常用厨具和默认份数。

请求示例：

```json
{
  "preferred_cuisines": ["家常菜"],
  "disliked_ingredients": ["香菜"],
  "allergies": [],
  "cooking_level": "easy",
  "appliances": ["炒锅", "电饭煲"],
  "default_servings": 2
}
```

## 7. 管理端基础数据接口

以下接口需要管理员登录。

```text
GET    /api/admin/categories
POST   /api/admin/categories
PUT    /api/admin/categories/{id}
DELETE /api/admin/categories/{id}

GET    /api/admin/tags
POST   /api/admin/tags
PUT    /api/admin/tags/{id}
DELETE /api/admin/tags/{id}

GET    /api/admin/ingredients
POST   /api/admin/ingredients
PUT    /api/admin/ingredients/{id}
DELETE /api/admin/ingredients/{id}
```

## 8. 认证接口

### POST `/api/auth/login`

请求：

```json
{
  "username": "admin",
  "password": "change-me"
}
```

成功后通过 HttpOnly Cookie 保存 Web 端登录状态，同时返回移动端使用的 `access_token`。移动端后续请求使用 `Authorization: Bearer <access_token>`。

响应示例：

```json
{
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "avatar": null,
    "role": "admin",
    "access_token": "..."
  },
  "message": "登录成功"
}
```

### POST `/api/auth/register`

注册普通家庭成员账号并自动登录。

```json
{
  "username": "family_member",
  "password": "至少 6 位密码",
  "nickname": "小明"
}
```

### POST `/api/auth/logout`

清除登录 Cookie。移动端同时清除本地保存的 Token。

### GET `/api/auth/me`

获取当前登录用户。

### PUT `/api/auth/profile`

修改当前用户昵称或头像路径。

## 9. 管理端菜谱接口

以下接口需要管理员登录。

### GET `/api/admin/recipes`

获取所有状态的菜谱，包括草稿和已下架菜谱。

### POST `/api/admin/recipes`

创建菜谱。

### GET `/api/admin/recipes/{recipe_id}`

获取管理端菜谱详情。

### PUT `/api/admin/recipes/{recipe_id}`

更新菜谱。

### DELETE `/api/admin/recipes/{recipe_id}`

删除菜谱。

### POST `/api/admin/recipes/{recipe_id}/publish`

发布菜谱。

### POST `/api/admin/recipes/{recipe_id}/archive`

下架菜谱。

## 10. 文件接口

### POST `/api/admin/uploads`

上传菜品或步骤图片。

请求类型：`multipart/form-data`

字段：

```text
file: 图片文件
kind: recipe_cover | recipe_step
```

响应：

```json
{
  "data": {
    "path": "/uploads/recipes/example.webp",
    "url": "/uploads/recipes/example.webp"
  },
  "message": "success"
}
```

## 11. 菜谱创建请求示例

```json
{
  "name": "番茄炒蛋",
  "description": "简单快速的家常菜。",
  "cover_image": "/uploads/recipes/tomato-egg.webp",
  "meal_type": "lunch",
  "category_id": 1,
  "difficulty": "easy",
  "cooking_time": 15,
  "servings": 2,
  "tips": "鸡蛋炒至刚凝固即可盛出。",
  "status": "published",
  "nutrition": {
    "calories": 450,
    "protein": 20,
    "carbs": 50,
    "fat": 15
  },
  "ingredients": [
    {
      "name": "番茄",
      "amount": 2,
      "unit": "个",
      "note": "切块"
    },
    {
      "name": "鸡蛋",
      "amount": 3,
      "unit": "个",
      "note": "打散"
    }
  ],
  "steps": [
    {
      "step_no": 1,
      "description": "番茄切块，鸡蛋打散。"
    },
    {
      "step_no": 2,
      "description": "先将鸡蛋炒熟后盛出。"
    }
  ],
  "tag_ids": [1, 2]
}
```
