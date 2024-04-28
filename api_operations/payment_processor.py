import paypalrestsdk


class CreditCardProcessor:
    def process_payment(self, payment_info):
        
        
        print(
            f"Processing credit card payment for {payment_info['amount']}...")

        return {'success': True, 'message': 'Credit card payment processed successfully'}


class BankTransferProcessor:
    def process_payment(self, payment_info):
        print(
            f"Processing bank transfer payment for {payment_info['amount']}...")

        return {'success': True, 'message': 'Bank transfer payment processed successfully'}


credit_card_processor = CreditCardProcessor()
bank_transfer_processor = BankTransferProcessor()


def process_payment(payment_info):
    payment_method = payment_info.get('method')

    if not payment_method:
        return {'success': False, 'message': 'No payment method provided'}

    if payment_method == 'paypal':
        # Simulate a successful PayPal payment
        print(f"Processing PayPal payment for {payment_info['amount']}...")
        return {'success': True, 'message': 'PayPal payment processed successfully'}

    elif payment_method == 'credit_card':
        # Process credit card payment
        result = credit_card_processor.process_payment(payment_info)
        return result

    elif payment_method == 'bank_transfer':
        # Process bank transfer
        result = bank_transfer_processor.process_payment(payment_info)
        return result

    else:
        return {'success': False, 'message': 'Invalid payment method'}