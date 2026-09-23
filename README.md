# Cooking

家用做饭助手：提供早餐、午餐、晚餐菜谱浏览、搜索、收藏和管理功能。

## 当前状态

当前已完成第一轮基础搭建：

- Vue 3 + TypeScript + Vite 前端骨架
- FastAPI 后端骨架
- Docker Compose 部署配置
- 数据模型设计文档
- API 接口约定文档
- SQLite 数据模型和初始化数据
- 管理员登录和菜谱 CRUD 接口
- 用户端菜谱列表、详情页
- 管理端菜谱录入页
- 收藏、饮食偏好和烹饪步骤模式
- 分类、标签和食材管理
- 内置 108 道初始化菜谱数据，覆盖八大菜系、西餐和烘焙

当前已经打通“管理员录入菜谱 → 用户端查看菜谱”的最小闭环。

## 快速启动

### 使用 Conda 创建本地开发环境

项目提供了本地镜像配置和环境定义。使用项目内环境目录，不需要修改全局 Conda 环境目录：

```bash
export CONDARC="$PWD/.condarc"
export CONDA_PKGS_DIRS=/private/tmp/cooking-conda-pkgs
conda env create --prefix "$PWD/.conda-env" -f environment.yml
```

启动后端：

```bash
conda run --prefix "$PWD/.conda-env" \
  uvicorn app.main:app --app-dir backend --reload --port 8000
```

前端需要单独安装 Node.js/npm，不使用 Conda：

```bash
cd frontend
npm install
npm run dev
```

### 使用 Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

启动后访问：

- 用户端：http://localhost:8080
- 后端健康检查：http://localhost:8000/api/health
- API 文档：http://localhost:8000/docs
- 管理端：http://localhost:8080/admin/recipes
- 基础数据：http://localhost:8080/admin/catalog

默认管理员账号：

```text
用户名：admin
密码：change-me
```

正式使用前请通过 `.env` 修改 `ADMIN_PASSWORD` 和 `SECRET_KEY`。

### 本地开发

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### Android / iOS 移动端

移动端基于 Capacitor 复用 Vue 前端。首次准备原生工程：

```bash
cd frontend
npm install
npx cap add android
npx cap add ios
```

移动端可以直接打包，首次打开时填写服务地址；也可以在构建时写入默认 API 地址：

```bash
VITE_API_BASE_URL=https://api.example.com npm run mobile:sync
```

然后使用 Android Studio 打开 `frontend/android`，或使用 Xcode 打开 `frontend/ios/App/App.xcodeproj`。完整说明见 [移动端接入说明](docs/mobile-app.md)。

## 项目结构

```text
.
├── backend/       # FastAPI 后端
├── data/          # SQLite 数据库和图片目录
├── deploy/        # Nginx 配置
├── docs/          # 数据模型和 API 文档
├── frontend/      # Vue 前端
└── docker-compose.yml
```

## 开发约定

- API 统一使用 `/api` 前缀。
- 数据库迁移文件由后端统一维护。
- 前端先依据 `docs/api.md` 使用 Mock 数据开发。
- 不将真实数据库文件和上传图片提交到 Git。
- 第一版默认只在局域网内使用。

## 第一版已实现功能

- 早餐、午餐、晚餐菜谱浏览
- 菜名和食材搜索
- 难度、烹饪时间筛选
- 菜谱详情、食材和制作步骤
- 烹饪模式和步骤计时
- 管理员菜谱新增、编辑、删除、发布和下架
- 菜谱封面图片上传
- 收藏和收藏列表
- 用户饮食偏好设置
- 分类、标签和食材管理

初始化菜谱位于 [backend/seed/recipes.json](backend/seed/recipes.json)，应用首次启动时自动导入；重复启动会按菜名跳过已有菜谱，数据文件设置了 100 GiB 大小上限。

## 数据库迁移

应用启动时会自动创建缺失的数据表。需要显式执行迁移时，可以运行：

```bash
cd backend
alembic upgrade head
```
