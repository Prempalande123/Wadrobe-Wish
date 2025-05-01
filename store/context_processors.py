# store/context_processors.py

def customer_name(request):
    """
    Adds 'customer_name' to the context of all templates automatically.
    This pulls from the session if the user is authenticated.
    """
    customer_name = None
    if request.user.is_authenticated:
        customer_name = request.session.get('customer_name', request.user.username)
    return {
        'customer_name': customer_name
    }
