import pika
import xml.etree.ElementTree as ET

RABBITMQ_HOST = "murabbitmq.ghhsdadqfycscha9.northcentralus.azurecontainer.io"
RABBITMQ_USER = "tmjg5h"
RABBITMQ_PASS = "tmjg5h"

STUDENT_A_PAWPRINT = "tmjg5h"
STUDENT_B_PAWPRINT = "tmjg5h"

STEP0_EXCHANGE = "STEP0_WORK_EXCHANGE"
STEP1_EXCHANGE = "STEP1_WORK_EXCHANGE"
STEP0_QUEUE = "tmjg5h_STEP0"


def make_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=5672,
        virtual_host="/",
        credentials=credentials
    )
    return pika.BlockingConnection(params)


def process_message(body):
    text = body.decode()
    print("[Student A] Raw message:")
    print(text)

    root = ET.fromstring(text)

    # ONLY process Add or Multiply
    if root.tag not in ("Mult", "Add", "Multiply"):
        print(f"[Student A] Ignoring message with tag <{root.tag}>")
        return None

    operands = root.findall("Operand")
    if len(operands) != 2:
        print("[Student A] Bad operand count, ignoring")
        return None

    a = int(operands[0].text)
    b = int(operands[1].text)

    if root.tag == "Add":
        return a + b
    else:  # Mult
        return a * b



def make_factorial_xml(n):
    root = ET.Element("Factorial")
    op = ET.SubElement(root, "Operand")
    op.text = str(n)
    return ET.tostring(root).decode()


def main():
    connection = make_connection()
    channel = connection.channel()

    channel.exchange_declare(exchange=STEP0_EXCHANGE, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=STEP1_EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=STEP0_QUEUE, durable=True)

    channel.queue_bind(queue=STEP0_QUEUE, exchange=STEP0_EXCHANGE, routing_key=STUDENT_A_PAWPRINT)

    print("[Student A] Waiting for messages...")

    def callback(ch, method, properties, body):
        result = process_message(body)

        print(f"[Student A] Computed: {result}")

        factorial_xml = make_factorial_xml(result)

        ch.basic_publish(
            exchange=STEP1_EXCHANGE,
            routing_key=STUDENT_B_PAWPRINT,
            body=factorial_xml,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)



    channel.basic_consume(queue=STEP0_QUEUE, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()
