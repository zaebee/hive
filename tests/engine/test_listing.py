import os
import shutil
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_list_command():
    runner = CliRunner()

    # Test data
    components_to_create = [
        {'name': 'component_a', 'domain': 'domain_1', 'type': 'aggregate'},
        {'name': 'component_b', 'domain': 'domain_1', 'type': 'transformation'},
        {'name': 'component_c', 'domain': 'domain_2', 'type': 'aggregate'},
    ]

    domains_to_clean = {'domain_1', 'domain_2'}

    # Clean up from previous runs
    for domain in domains_to_clean:
        domain_path = os.path.join('hive', 'components', domain)
        if os.path.exists(domain_path):
            shutil.rmtree(domain_path)

    try:
        # 1. Hatch the components
        for comp in components_to_create:
            result = runner.invoke(
                genesis,
                ['hatch', comp['type'], comp['name'], '--domain', comp['domain']],
                catch_exceptions=False
            )
            assert result.exit_code == 0

        # 2. Test `genesis list` (no filters)
        result_list_all = runner.invoke(genesis, ['list'], catch_exceptions=False)
        assert result_list_all.exit_code == 0
        output = result_list_all.output
        assert 'component_a' in output
        assert 'component_b' in output
        assert 'component_c' in output
        assert 'domain_1' in output
        assert 'domain_2' in output

        # 3. Test `genesis list --domain`
        result_list_domain = runner.invoke(genesis, ['list', '--domain', 'domain_1'], catch_exceptions=False)
        assert result_list_domain.exit_code == 0
        output_domain = result_list_domain.output
        assert 'component_a' in output_domain
        assert 'component_b' in output_domain
        assert 'component_c' not in output_domain

        # 4. Test `genesis list --type aggregate`
        result_list_type_agg = runner.invoke(genesis, ['list', '--type', 'aggregate'], catch_exceptions=False)
        assert result_list_type_agg.exit_code == 0
        output_type_agg = result_list_type_agg.output
        assert 'component_a' in output_type_agg
        assert 'component_b' not in output_type_agg
        assert 'component_c' in output_type_agg

        # 5. Test `genesis list --type transformation`
        result_list_type_trans = runner.invoke(genesis, ['list', '--type', 'transformation'], catch_exceptions=False)
        assert result_list_type_trans.exit_code == 0
        output_type_trans = result_list_type_trans.output
        assert 'component_a' not in output_type_trans
        assert 'component_b' in output_type_trans
        assert 'component_c' not in output_type_trans

        # 6. Test with a type that doesn't exist
        result_list_notype = runner.invoke(genesis, ['list', '--type', 'saga'], catch_exceptions=False)
        assert result_list_notype.exit_code == 0
        assert "No components found matching the criteria" in result_list_notype.output

    finally:
        # Cleanup
        for domain in domains_to_clean:
            domain_path = os.path.join('hive', 'components', domain)
            if os.path.exists(domain_path):
                shutil.rmtree(domain_path)
