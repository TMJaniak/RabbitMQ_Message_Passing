import pika
import xml.etree.ElementTree as ET
import math

RABBITMQ_HOST = "murabbitmq.ghhsdadqfycscha9.northcentralus.azurecontainer.io"
RABBITMQ_USER = "tmjg5h"
RABBITMQ_PASS = "tmjg5h"

STUDENT_A_PAWPRINT = "tmjg5h"
STUDENT_B_PAWPRINT = "tmjg5h"

STEP1_EXCHANGE = "STEP1_WORK_EXCHANGE"
STEP2_EXCHANGE = "STEP2_WORK_EXCHANGE"
STEP1_QUEUE = "tmjg5h_STEP1"


def make_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=5672,
        virtual_host="/",
        credentials=credentials
    )
    return pika.BlockingConnection(params)


def make_output_xml(result):
    root = ET.Element("Output")

    r = ET.SubElement(root, "Result")
    r.text = str(result)

    a = ET.SubElement(root, "StudentA")
    a.text = STUDENT_A_PAWPRINT

    b = ET.SubElement(root, "StudentB")
    b.text = STUDENT_B_PAWPRINT

    return ET.tostring(root).decode()


def main():
    connection = make_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=STEP1_EXCHANGE, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=STEP2_EXCHANGE, exchange_type="direct", durable=True)

    channel.queue_declare(queue=STEP1_QUEUE, durable=True)
    channel.queue_bind(queue=STEP1_QUEUE, exchange=STEP1_EXCHANGE, routing_key=STUDENT_B_PAWPRINT)

    print("[Student B] Waiting for factorial messages...")

    def callback(ch, method, properties, body):
        root = ET.fromstring(body.decode())
        n = int(root.find("Operand").text)

        print(f"[Student B] Computing {n}!")
        result = math.factorial(n)

        output_xml = make_output_xml(result)

        ch.basic_publish(
            exchange=STEP2_EXCHANGE,
            routing_key="",
            body=output_xml,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=STEP1_QUEUE, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()
