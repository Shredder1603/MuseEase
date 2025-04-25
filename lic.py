import json 
with open("pygame.json") as fp:
    data = json.load(fp)
    
licenses = set()
for component in data.get('components', []):
    for license_info in component.get('licenses', []):
        license = license_info.get('license', {})
        license_id = license.get('id')
        if license_id:
            licenses.add(license_id)

print(licenses)