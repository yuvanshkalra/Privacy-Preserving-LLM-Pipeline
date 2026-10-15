from faker import Faker
import random

fake = Faker("en_IN")


def generate_aadhar():
    """Generate a fake 12-digit Aadhar number in XXXX-XXXX-XXXX format."""
    parts = [str(random.randint(1000, 9999)) for _ in range(3)]
    return "-".join(parts)


def generate_contract():
    name = fake.name()
    phone = fake.phone_number()
    email = fake.email()
    aadhar = generate_aadhar()

    address = fake.address().replace("\n", ", ")
    company = fake.company()
    job_title = fake.job()
    salary = f"INR {random.randint(30, 150) * 1000:,} per annum"
    start_date = fake.date_between(start_date="+7d", end_date="+60d").strftime(
        "%d %B %Y"
    )
    contract_date = fake.date_this_year().strftime("%d %B %Y")

    contract = f"""
EMPLOYMENT CONTRACT
===================

This Employment Contract ("Agreement") is entered into on {contract_date}, by and between:

EMPLOYER:
  Company Name : {company}
  Registered Address : {fake.address().replace(chr(10), ", ")}

EMPLOYEE:
  Full Name    : {name}
  Address      : {address}
  Phone Number : {phone}
  Email        : {email}
  Aadhar Number: {aadhar}

---

1. POSITION AND DUTIES
   The Employer agrees to employ the Employee in the capacity of {job_title}.
   The Employee shall perform all duties as assigned by the management of {company}.

2. COMMENCEMENT DATE
   This Agreement shall commence on {start_date} and shall continue unless terminated
   by either party in accordance with the terms set forth herein.

3. COMPENSATION
   The Employee will be entitled to a gross salary of {salary}, payable in equal
   monthly instalments on the last working day of each month.

4. WORKING HOURS
   The standard working hours shall be 9:00 AM to 6:00 PM, Monday through Friday.
   The Employee may be required to work additional hours as necessary.

5. LEAVE ENTITLEMENT
   The Employee is entitled to:
   - 12 days of earned leave per year
   - 12 days of casual/sick leave per year
   - Public holidays as per the company calendar

6. CONFIDENTIALITY
   The Employee agrees to keep all proprietary information, trade secrets, and
   business data of {company} strictly confidential during and after employment.

7. TERMINATION
   Either party may terminate this Agreement by providing 30 days' written notice.
   The Employer reserves the right to terminate employment immediately in cases of
   gross misconduct.

8. GOVERNING LAW
   This Agreement shall be governed by and construed in accordance with the laws
   of the Republic of India. Any disputes shall be subject to the jurisdiction of
   courts located in {fake.city()}.

---

IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date
first written above.

EMPLOYER                                EMPLOYEE

_______________________                 _______________________
Authorised Signatory                    {name}
{company}                               Aadhar: {aadhar}

"""
    return contract


if __name__ == "__main__":
    output_file = "sample_contract.txt"
    contract_text = generate_contract()

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(contract_text)

    print(f"Contract generated and saved to '{output_file}'.")
