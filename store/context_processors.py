from .models import Cart

def cart_count(request):
    session_id = request.session.session_key
    count = 0

    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    cart = Cart.objects.filter(session_id=session_id).first()

    if cart:
        count = sum(item.quantity for item in cart.items.all())

    return {"cart_count": count}