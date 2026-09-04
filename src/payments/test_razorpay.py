from razorpay_client import create_test_order


def main():

    print("Creating Razorpay Test Mode order...")

    order = create_test_order(
        amount=100.00
    )

    print("\nSUCCESS!")
    print("-----------------------------")
    print("Order ID:", order["id"])
    print("Amount:", order["amount"])
    print("Currency:", order["currency"])
    print("Status:", order["status"])
    print("-----------------------------")


if __name__ == "__main__":
    main()