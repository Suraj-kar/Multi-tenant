with open(r'e:\prix\organization\templates\core\update_tenant.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of the incorrect syntax
content = content.replace('client.status=="ACTIVE"', 'client.status == "ACTIVE"')
content = content.replace('client.status=="ONBOARDING"', 'client.status == "ONBOARDING"')
content = content.replace('client.status=="SUSPENDED"', 'client.status == "SUSPENDED"')
content = content.replace('client.status=="TERMINATED"', 'client.status == "TERMINATED"')

with open(r'e:\prix\organization\templates\core\update_tenant.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template fixed successfully!")
