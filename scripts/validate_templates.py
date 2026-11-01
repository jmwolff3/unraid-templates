"""Validate repository metadata and Unraid v2 templates with the stdlib."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/jmwolff3/unraid-templates'
RAW = 'https://raw.githubusercontent.com/jmwolff3/unraid-templates/main/'
errors = []


def check(ok, path, message):
    if not ok:
        errors.append(f'{path.relative_to(ROOT)}: {message}')


def required(root, names, path):
    for name in names:
        check(bool((root.findtext(name) or '').strip()), path, f'missing {name}')


def validate():
    templates = sorted((ROOT / 'templates').glob('*.xml'))
    check(bool(templates), ROOT / 'templates', 'no Docker templates')
    for path in sorted(ROOT.rglob('*.xml')):
        try:
            text = path.read_text()
            root = ET.fromstring(text)
        except (ET.ParseError, UnicodeError) as exc:
            check(False, path, str(exc))
            continue
        check(not re.search(r'YOUR_[A-Z_]+|example\.(?:com|org|net)|\b(?:placeholder|REPLACE ME)\b', text, re.I), path, 'starter placeholder found')
        for node in root.iter():
            value = (node.text or '').strip()
            if value.startswith(('http://', 'https://')) and node.tag != 'WebUI':
                try:
                    parsed = urlparse(value)
                    check(bool(parsed.netloc), path, f'invalid URL in {node.tag}')
                except ValueError:
                    check(False, path, f'invalid URL in {node.tag}')
        if path.name == 'ca_profile.xml':
            check(root.tag == 'CommunityApplications', path, 'invalid profile root')
            required(root, ['Profile', 'Icon', 'WebPage'], path)
            check(root.findtext('WebPage') == REPO, path, 'profile repository URL mismatch')
        elif path.parent.name == 'templates':
            check(root.tag == 'Container' and root.get('version') == '2', path, 'expected Container version 2')
            required(root, ['Name', 'Repository', 'Network', 'WebUI', 'Overview', 'Project', 'Icon', 'TemplateURL'], path)
            check(root.findtext('TemplateURL') == RAW + path.relative_to(ROOT).as_posix(), path, 'TemplateURL must match the exact main-branch file')
            configs = root.findall('Config')
            targets = [(c.get('Type'), c.get('Target')) for c in configs]
            check(len(targets) == len(set(targets)), path, 'duplicate Config targets')
            for c in configs:
                required_attrs = ['Name', 'Target', 'Default', 'Description', 'Type', 'Display', 'Required', 'Mask']
                check(all(a in c.attrib for a in required_attrs), path, 'incomplete Config attributes')
                check(c.get('Display') in ('always', 'advanced', 'hidden'), path, 'invalid Display')
                check(c.get('Type') in ('Port', 'Path', 'Variable', 'Label', 'Device'), path, 'invalid Config Type')
                for attr in ('Required', 'Mask'):
                    check(c.get(attr) in ('true', 'false'), path, f'invalid {attr}')
                if c.get('Type') == 'Port':
                    check(c.get('Mode') in ('tcp', 'udp'), path, 'invalid port protocol')
                if c.get('Target') in ('DATABASE_URL', 'JWT_SECRET', 'EMAIL_SMTP_PASSWORD'):
                    check(c.get('Mask') == 'true', path, 'credential must be masked')
                    check(not c.get('Default') and not (c.text or '').strip(), path, 'credential default must be empty')
            for port in re.findall(r'\[PORT:(\d+)\]', root.findtext('WebUI', '')):
                check(('Port', port) in targets, path, 'WebUI references an unmapped container port')
    check((ROOT / 'ca_profile.xml').is_file(), ROOT / 'ca_profile.xml', 'profile missing')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(templates)} Docker template(s) and repository XML.')
    return 0


if __name__ == '__main__':
    sys.exit(validate())
