from estimator.models import Estimate
from authentication.models import User

print("="*60)
print("DATABASE CHECK - ESTIMATES")
print("="*60)

# Check estimates
total = Estimate.objects.count()
print(f"\nTotal Estimates: {total}\n")

if total > 0:
    for estimate in Estimate.objects.all()[:10]:
        print(f"ID: {estimate.id} | Serial: {estimate.serial_number} | Client: {estimate.client_name}")
        print(f"  Status: {estimate.status} | Amount: ${estimate.charge_inc_tax} | Date: {estimate.date}")
        print(f"  Items: {estimate.items.count()}")
        print("-" * 60)
else:
    print("No estimates found")

print("\n" + "="*60)
print("ESTIMATOR USERS")
print("="*60 + "\n")

estimators = User.objects.filter(role__in=['Estimator', 'Admin', 'Super Admin'])
for user in estimators:
    print(f"{user.email} ({user.role})")
