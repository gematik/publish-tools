from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory

from publish_tools.handlers import ig_history, ig_list
from publish_tools.handlers.helper import version_key
from publish_tools.models.ig_list import IgList
from publish_tools.models.package_list import PackageList


class VersionLinks(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = 0
        self.links = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            assert 'open' not in dict(attrs)
            self.depth += 1
        if tag == 'a':
            self.links[dict(attrs)['href']] = self.depth > 0

    def handle_endtag(self, tag):
        if tag == 'details':
            self.depth -= 1


def test_numeric_and_prerelease_order():
    versions = ['1.9.0', '1.10.0-rc.2', '1.10.0', '1.10.0-rc.10']
    assert sorted(versions, key=version_key) == [
        '1.9.0', '1.10.0-rc.2', '1.10.0-rc.10', '1.10.0'
    ]


def test_list_groups_versions_by_package():
    guides = []
    for package in ['one', 'two']:
        guides.append(dict(
            name='Same title', npm_name=package, category='test',
            canonical='https://example.org/', ci_build='https://example.org/ci',
            description='Guide', editions=[dict(
                name='Release', ig_version=version,
                package=f'{package}#{version}', fhir_version=['4.0.1'],
                url=f'https://example.org/{package}/{version}',
                description='<script>unsafe</script>',
            ) for version in ['1.9.0', '1.10.0']],
        ))
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=guides))
        html = (Path(directory) / 'index.html').read_text()
    links = VersionLinks(html).links
    for package in ['one', 'two']:
        assert links[f'https://example.org/{package}/1.10.0'] is False
        assert links[f'https://example.org/{package}/1.9.0'] is True
    assert '<script>unsafe</script>' not in html
    assert 'Datum unbekannt' in html


def test_history_prefers_current_release_and_keeps_ci_separate():
    plist = PackageList.model_validate(dict(
        package_id='example', canonical='https://example.org/', title='Example',
        introduction='Test', list=[
            dict(path='https://example.org/ci', desc='CI'),
            *[dict(version=version, path=f'https://example.org/{version}',
                   desc='Release', status='release', current=current,
                   date='2026-01-01', sequence='Release', fhir_version='4.0.1')
              for version, current in [('1.9.0', True), ('1.10.0', False)]],
        ],
    ))
    with TemporaryDirectory() as directory:
        ig_history.render(Path(directory), plist)
        html = (Path(directory) / 'index.html').read_text()
    links = VersionLinks(html).links
    assert links['https://example.org/1.9.0'] is False
    assert links['https://example.org/1.10.0'] is True
    assert links['https://example.org/ci'] is False
    assert 'Veröffentlicht: <time datetime="2026-01-01">01.01.2026</time>' in html
    assert 'Release ·' not in html


def test_empty_list_and_history_render():
    with TemporaryDirectory() as directory:
        path = Path(directory)
        ig_list.render(path, IgList())
        assert 'Noch keine Pakete' in (path / 'index.html').read_text()
        ig_history.render(path, PackageList(
            package_id='example', canonical='https://example.org/',
            title='Example', introduction='Test',
        ))
        assert 'Noch keine Version' in (path / 'index.html').read_text()


def test_package_groups_combine_sequences_and_keep_previews_separate():
    editions = []
    for sequence, versions in [
        ('Sequence A', ['1.9.0', '1.10.0', '2.0.0-ballot.1', '2.0.0-ballot.2',
                        '2.0.0-rc.1', '2.0.0-rc.2']),
        ('Sequence B', ['3.0.0']),
    ]:
        for version in versions:
            editions.append(dict(name=sequence, ig_version=version,
                package=f'example#{version}', fhir_version=['4.0.1'],
                url=f'https://example.org/{version}', description=sequence))
    guide = dict(name='Example', npm_name='example', category='test',
        canonical='https://example.org/', ci_build='https://example.org/ci',
        description='Guide', editions=editions)
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=[guide]))
        html = (Path(directory) / 'index.html').read_text()
    links = VersionLinks(html).links
    for version in ['2.0.0-ballot.2', '2.0.0-rc.2', '3.0.0']:
        assert links[f'https://example.org/{version}'] is False
    for version in ['1.9.0', '1.10.0', '2.0.0-ballot.1', '2.0.0-rc.1']:
        assert links[f'https://example.org/{version}'] is True
    assert 'Sequence A' in html and 'Sequence B' in html
    assert 'Ballot' in html and 'Release Candidate' in html


def test_preview_detection_from_sequence_and_version():
    from publish_tools.handlers.helper import release_channel
    assert release_channel('1.0.0', 'Example Ballot') == 'Ballot'
    assert release_channel('1.0.0', 'Example RC 2') == 'Release Candidate'
    assert release_channel('1.0.0-b1') == 'Ballot'
    assert release_channel('1.0.0-RC1') == 'Release Candidate'
    assert release_channel('1.0.0', 'Beschreibung') == 'Veröffentlichungen'


def test_ballots_before_release_date_remain_visible():
    versions = [
        ('2.0.0', '2026-06-01', 'release'),
        ('3.0.0-ballot.1', '2026-05-01', 'ballot'),
        ('3.0.0-ballot.2', '2026-07-01', 'ballot'),
        ('3.0.0-ballot.3', '2026-08-01', 'ballot'),
    ]
    guide = dict(name='Example', npm_name='example', category='test',
        canonical='https://example.org/', ci_build='https://example.org/ci',
        description='Guide', editions=[dict(name='Sequence', ig_version=v,
        package=f'example#{v}', fhir_version=['4.0.1'], date=d, status=status,
        url=f'https://example.org/{v}', description='Release') for v,d,status in versions])
    with TemporaryDirectory() as directory:
        ig_list.render(Path(directory), IgList(guides=[guide]))
        html = (Path(directory) / 'index.html').read_text()
    links = VersionLinks(html).links
    assert links['https://example.org/2.0.0'] is False
    assert links['https://example.org/3.0.0-ballot.1'] is False
    assert links['https://example.org/3.0.0-ballot.2'] is True
    assert links['https://example.org/3.0.0-ballot.3'] is False
    assert html.count('class="package-id"') == 1
    assert 'alt="gematik"' in html
    assert 'Veröffentlicht: <time datetime="2026-06-01">01.06.2026</time>' in html
    assert 'Sequence' not in html


def test_from_history_includes_current_build():
    from publish_tools.handlers.package_list import from_history
    from publish_tools.models.guide import Guide
    guide = Guide(name='Example', npm_name='example', category='test',
        canonical='https://example.org/', ci_build='https://example.org/build',
        description='Guide', editions=[])
    plist = from_history(guide)
    assert len(plist.list) == 1
    assert plist.list[0].version == 'current'
    assert plist.list[0].current is True
    with TemporaryDirectory() as directory:
        ig_history.render(Path(directory), plist)
        html = (Path(directory) / 'index.html').read_text()
    assert 'Current' in html
    assert 'https://example.org/build' in html
    assert VersionLinks(html).links['https://example.org/build'] is False
