import pandas as pd
import redis
import json
from flask import Flask, jsonify, render_template

# 初始化Redis连接
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def load_data_to_redis(json_file='合并后的电影信息.json'):
    """从JSON文件加载数据到Redis"""
    df = pd.read_json(json_file, orient='records')
    data = df.to_dict('records')
    r.delete('movie_data')  # 清空旧数据
    for item in data:
        r.lpush('movie_data', json.dumps(item))
    print("数据已成功加载到Redis")

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 注册路由
    @app.route('/api/movies')
    def get_movies():
        data = r.lrange('movie_data', 0, -1)
        return jsonify([json.loads(item) for item in data])
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

# 创建应用实例
app = create_app()

# 手动调用初始化函数（确保在应用启动后执行）
if __name__ == '__main__':
    load_data_to_redis()  # 启动时加载数据
    app.run(debug=True)