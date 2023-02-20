import threading
import pika, sys, os
from flask import Flask
import urllib.request, json

url = "https://api.themoviedb.org/3/discover/movie?api_key={}".format(os.environ.get("TMDB_API_KEY"))


app = Flask(__name__)

@app.route("/hello")
def status():
    return "C'est dohi"

def start_consumer():
    url = os.environ.get('CLOUDAMQP_URL', 'urlrabittmq')
    params = pika.URLParameters(url)
    try:
        connection = pika.BlockingConnection(params)
    except pika.exceptions.AMQPConnectionError as exc:
        print("Failed to connect to RabbitMQ service. Message wont be sent.")
        return
    channel = connection.channel()

    channel.queue_declare(queue='order', durable=True)

    print(' Waiting for messages...')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='order', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()

consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.daemon = True
consumer_thread.start()

if __name__ == "__main__":
    try:
        app.run(debug=True)
        print('apppp run')
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)