from __init__ import create_app
from utils.data import init_pa

app = create_app()

if __name__ == '__main__':
    init_pa()
    app.run(host='0.0.0.0',port=5555)