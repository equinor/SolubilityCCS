# Branch Protection Configuration

This document describes the recommended branch protection rules for this repository.

## Main/Master Branch Protection

### Required Status Checks
The following checks must pass before merging to main:

1. **Required Tests** - All core functionality tests
2. **Acid Formation Analysis Tests** - Specific H2SO4 and HNO3 tests
3. **Tests** - Full test suite (optional, but recommended)

### Settings to Enable in GitHub

1. **Require status checks to pass before merging**: ✅
   - Require branches to be up to date before merging: ✅
   - Required status checks:
     - `Required Acid Formation Tests / required-acid-formation-tests`
     - `Acid Formation Analysis Tests / acid-formation-tests`

2. **Require pull request reviews before merging**: ✅ (recommended)
   - Required approving reviews: 1
   - Dismiss stale reviews when new commits are pushed: ✅

3. **Require conversation resolution before merging**: ✅

4. **Require signed commits**: ⚪ (optional)

5. **Require linear history**: ⚪ (optional)

6. **Include administrators**: ✅ (recommended)

7. **Restrict pushes that create files**: ⚪ (optional)

## How to Set Up

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar
4. Click **Add rule** or edit existing rule for `main`/`master`
5. Configure the settings as described above

## Automatic Test Triggers

Tests will automatically run on:
- Pull requests to main/master/develop branches
- Pushes to main/master/develop branches
- Changes to specific files (fluid.py, test_fluid.py, etc.)

## Manual Test Execution

To run the required tests locally:

```bash
# Activate virtual environment
source venv/bin/activate

# Run specific required tests
python -m pytest test_fluid.py::TestAcidFormationAnalysis::test_h2so4_acid_formation_analysis_specific_case -v
python -m pytest test_fluid.py::TestAcidFormationAnalysis::test_hno3_acid_formation_analysis_specific_case -v

# Run all acid formation tests
python -m pytest test_fluid.py::TestAcidFormationAnalysis -v

# Run all tests
python -m pytest -v
```
