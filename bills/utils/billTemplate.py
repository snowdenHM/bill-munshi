from django.shortcuts import get_object_or_404

from bills.models import ZohoBill, ZohoProduct


def tableDataProcessing(data):
    desired_headers = ["SI No.", "Description of Goods", "HSN/SAC", "Quantity", "Rate", "per", "Amount"]
    zohoBill = get_object_or_404(ZohoBill, selectBill=data)
    # Find the table with desired headers
    desired_table = None
    for table_name, table_data in data.tableData.items():
        # Check if the first row of the table matches the desired headers
        if table_data[0] == desired_headers:
            desired_table = table_data
            break
    if desired_table:
        # Create lists to store valid rows
        valid_product_rows = []
        valid_total_value = []
        valid_igst_value = []

        # Iterate over the rows in the desired table and check for valid data
        for row in desired_table[1:]:  # Exclude the header row
            si_no, description, hsn_sac, quantity, rate, per, amount = row

            if description == "IGST OUTPUT":
                valid_igst_value.append(row)
            elif description == "Total":
                valid_total_value.append(row)
            else:
                valid_product_rows.append(row)

        # Check if there are valid rows in valid_product_rows
        if valid_product_rows:
            for row in valid_product_rows:
                si_no, description, hsn_sac, quantity, rate, per, amount = row
                product = ZohoProduct(
                    zohoBill=zohoBill,
                    item_name=si_no,
                    item_details=description,
                    chart_of_accounts=None,
                    taxes=None,
                    rate=rate,
                    quantity=quantity.replace('KGS', '').replace(',', '').strip(),
                    amount=amount.replace('₹', '').replace(',', '').strip(),  # Parse amount
                )
                product.save()

        # Check if there are valid rows in valid_total_value
        if valid_total_value:
            for row in valid_total_value:
                si_no, description, hsn_sac, quantity, rate, per, amount = row
                zohoBill.total = amount.replace('₹', '').replace(',', '').strip()
                zohoBill.save(update_fields=['total'])
                print("Zoho Bill Updated")

        # Check if there are valid rows in valid_igst_value
        if valid_igst_value:
            for row in valid_igst_value:
                si_no, description, hsn_sac, quantity, rate, per, amount = row
                zohoBill.igst = amount.replace('₹', '').replace(',', '').strip()
                zohoBill.save(update_fields=['igst'])
                print("Zoho Bill Updated")
    else:
        print("Desired table not found in the JSON data.")
    return "Table Data Processing Done"


def formDataProcessing(data):
    print(data.formData)
    invoiceNo = data.formData.get('Invoice No.')
    billDate = data.formData.get('Dated')
    zohoBill = get_object_or_404(ZohoBill, selectBill=data)
    zohoBill.bill_no = invoiceNo
    zohoBill.bill_date = billDate
    zohoBill.save(update_fields=['bill_no', 'bill_date'])
    return "Form Data Processing Done"
