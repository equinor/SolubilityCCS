# Code Ownership and Review Process

This repository uses GitHub's CODEOWNERS feature to ensure proper code review and maintain code quality.

## Code Owner

The repository owner is responsible for:
- Reviewing all pull requests
- Maintaining code quality standards
- Ensuring test coverage
- Approving architectural changes

## Review Process

### Automatic Review Requests

When you create a pull request, the following happens automatically:
1. **CODEOWNERS file** triggers review request to the repository owner
2. **Required status checks** must pass before merging
3. **Branch protection rules** enforce the review process

### Required Reviews

All pull requests require:
- ✅ **Code owner approval** - Automatic via CODEOWNERS
- ✅ **Passing tests** - H2SO4 and HNO3 acid formation analysis tests
- ✅ **Clean build** - No compilation or lint errors

### Files Requiring Special Review

Critical files that always require code owner review:
- `fluid.py` - Core fluid simulation logic
- `neqsim_functions.py` - NeqSim integration functions
- `sulfuric_acid_activity.py` - Acid activity calculations
- `test_*.py` - All test files
- `Database/*.csv` - Database files
- `.github/` - Workflow and configuration files

## How to Get Your PR Reviewed

1. **Create your pull request** as normal
2. **Fill out the PR template** completely
3. **Ensure all tests pass** before requesting review
4. **Wait for automatic review request** to the code owner
5. **Address any feedback** promptly

## Contact

If you have questions about the review process or need urgent review:
- Tag the code owner in your PR comments
- Ensure your PR follows the template requirements
- Check that all automated tests are passing

## Emergency Changes

For critical bug fixes or security issues:
1. Create PR as normal
2. Mark as urgent in the title: `[URGENT] Fix critical bug in...`
3. Tag the code owner directly
4. Provide detailed explanation of the urgency

---

Remember: The code owner review requirement helps maintain the high quality and reliability of the acid formation analysis system.
