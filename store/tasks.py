import os
import django
from reportlab.pdfgen import canvas
from django.conf import settings


def generate_invoice(order_id):

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
    django.setup()

    from .models import Order

    order = Order.objects.get(id=order_id)

    invoice_path = os.path.join(settings.MEDIA_ROOT, f"invoices/order_{order.id}.pdf")

    c = canvas.Canvas(invoice_path)

    c.drawString(100, 800, f"Invoice for Order #{order.id}")
    c.drawString(100, 770, f"Customer: {order.user}")
    c.drawString(100, 740, f"Total Amount: ${order.total_price}")
    c.drawString(100, 710, f"Payment ID: {order.razorpay_payment_id}")

    c.save()

    order.invoice = f"invoices/order_{order.id}.pdf"
    order.save()

    print("PDF Invoice Generated")