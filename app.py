from project import create_app, make_celery

app = create_app()
celery = make_celery(app)

if __name__ == "__main__":
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )