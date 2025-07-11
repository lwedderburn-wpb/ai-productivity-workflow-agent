#!/usr/bin/env python3
"""
Comprehensive Test Runner for GIS Ticket Management AI Agent

This script runs all test suites:
- Unit Tests: Core functionality testing
- Security Tests: Security validation and vulnerability checks  
- Functional Tests: End-to-end workflow testing

Usage:
    python run_tests.py [--unit] [--security] [--functional] [--all] [--verbose]
    
Examples:
    python run_tests.py --all           # Run all test suites
    python run_tests.py --unit          # Run only unit tests
    python run_tests.py --security      # Run only security tests
    python run_tests.py --functional    # Run only functional tests
    python run_tests.py --unit --security --verbose  # Run unit and security tests with verbose output
"""

import unittest
import sys
import os
import argparse
import time
from datetime import datetime
import json

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test modules
from tests.test_unit import TestEnhancedGISTicketAgent, TestXMLTicketParser, TestFlaskApp
from tests.test_security import TestSecurityValidation, TestAuthenticationSecurity
from tests.test_functional import TestFunctionalWorkflows

class TestRunner:
    """Comprehensive test runner with reporting capabilities"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            'unit': None,
            'security': None,
            'functional': None
        }
        self.start_time = datetime.now()
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add unit test classes
        suite.addTests(loader.loadTestsFromTestCase(TestEnhancedGISTicketAgent))
        suite.addTests(loader.loadTestsFromTestCase(TestXMLTicketParser))
        suite.addTests(loader.loadTestsFromTestCase(TestFlaskApp))
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if self.verbose else 1,
            stream=sys.stdout,
            buffer=True
        )
        
        result = runner.run(suite)
        self.results['unit'] = result
        
        print(f"\n📊 Unit Test Results:")
        print(f"   Tests Run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        return result.wasSuccessful()
    
    def run_security_tests(self):
        """Run security tests"""
        print("\n🔒 Running Security Tests...")
        print("=" * 50)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add security test classes
        suite.addTests(loader.loadTestsFromTestCase(TestSecurityValidation))
        suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationSecurity))
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if self.verbose else 1,
            stream=sys.stdout,
            buffer=True
        )
        
        result = runner.run(suite)
        self.results['security'] = result
        
        print(f"\n🛡️ Security Test Results:")
        print(f"   Tests Run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Security Score: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        # Highlight security issues
        if result.failures or result.errors:
            print("\n⚠️ SECURITY ISSUES DETECTED:")
            for test, trace in result.failures + result.errors:
                print(f"   - {test}")
        
        return result.wasSuccessful()
    
    def run_functional_tests(self):
        """Run functional tests"""
        print("\n🔄 Running Functional Tests...")
        print("=" * 50)
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add functional test classes
        suite.addTests(loader.loadTestsFromTestCase(TestFunctionalWorkflows))
        
        # Run tests
        runner = unittest.TextTestRunner(
            verbosity=2 if self.verbose else 1,
            stream=sys.stdout,
            buffer=True
        )
        
        result = runner.run(suite)
        self.results['functional'] = result
        
        print(f"\n🎯 Functional Test Results:")
        print(f"   Tests Run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Workflow Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        return result.wasSuccessful()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        print(f"🕐 Test Duration: {duration.total_seconds():.2f} seconds")
        print(f"📅 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate totals
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for test_type, result in self.results.items():
            if result:
                total_tests += result.testsRun
                total_failures += len(result.failures)
                total_errors += len(result.errors)
        
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_tests - total_failures - total_errors}")
        print(f"   Failed: {total_failures}")
        print(f"   Errors: {total_errors}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Individual test suite results
        print(f"\n📋 TEST SUITE BREAKDOWN:")
        for test_type, result in self.results.items():
            if result:
                suite_success = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
                status = "✅ PASS" if result.wasSuccessful() else "❌ FAIL"
                print(f"   {test_type.capitalize():12} | {result.testsRun:3} tests | {suite_success:5.1f}% | {status}")
        
        # Quality assessment
        print(f"\n🏆 QUALITY ASSESSMENT:")
        if success_rate >= 95:
            print("   🥇 EXCELLENT - Production ready!")
        elif success_rate >= 85:
            print("   🥈 GOOD - Minor issues to address")
        elif success_rate >= 70:
            print("   🥉 FAIR - Several issues need attention")
        else:
            print("   ⚠️ POOR - Significant issues require immediate attention")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if total_failures > 0:
            print(f"   🔧 Fix {total_failures} failing test(s)")
        if total_errors > 0:
            print(f"   🐛 Resolve {total_errors} error(s)")
        if success_rate < 100:
            print("   📈 Improve test coverage")
            print("   🔍 Review failed tests for system issues")
        
        # Security-specific recommendations
        security_result = self.results.get('security')
        if security_result and not security_result.wasSuccessful():
            print("   🛡️ Address security vulnerabilities immediately")
            print("   🔒 Review authentication and input validation")
        
        return success_rate >= 85
    
    def save_report_json(self, filename='test_report.json'):
        """Save test results as JSON for CI/CD integration"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'results': {}
        }
        
        for test_type, result in self.results.items():
            if result:
                report['results'][test_type] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                    'passed': result.wasSuccessful()
                }
        
        # Calculate overall metrics
        total_tests = sum(r['tests_run'] for r in report['results'].values())
        total_failures = sum(r['failures'] for r in report['results'].values())
        total_errors = sum(r['errors'] for r in report['results'].values())
        
        report['summary'] = {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0,
            'all_passed': all(r['passed'] for r in report['results'].values())
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Test report saved to: {filename}")


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(
        description='Comprehensive Test Runner for GIS Ticket Management AI Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all test suites
  python run_tests.py --unit                   # Run only unit tests
  python run_tests.py --security               # Run only security tests
  python run_tests.py --functional             # Run only functional tests
  python run_tests.py --unit --security -v     # Run unit and security tests with verbose output
  python run_tests.py --all --save-report      # Run all tests and save JSON report
        """
    )
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--security', action='store_true', help='Run security tests')
    parser.add_argument('--functional', action='store_true', help='Run functional tests')
    parser.add_argument('--all', action='store_true', help='Run all test suites')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--save-report', action='store_true', help='Save JSON test report')
    
    args = parser.parse_args()
    
    # Default to all tests if no specific suite is selected
    if not any([args.unit, args.security, args.functional, args.all]):
        args.all = True
    
    # If --all is specified, enable all test types
    if args.all:
        args.unit = True
        args.security = True
        args.functional = True
    
    # Initialize test runner
    runner = TestRunner(verbose=args.verbose)
    
    print("🚀 GIS Ticket Management AI Agent - Test Suite")
    print("=" * 80)
    print(f"⏰ Started: {runner.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Running: ", end="")
    suites = []
    if args.unit: suites.append("Unit")
    if args.security: suites.append("Security") 
    if args.functional: suites.append("Functional")
    print(", ".join(suites) + " Tests")
    
    # Run selected test suites
    success = True
    
    if args.unit:
        success &= runner.run_unit_tests()
    
    if args.security:
        success &= runner.run_security_tests()
    
    if args.functional:
        success &= runner.run_functional_tests()
    
    # Generate and display report
    overall_success = runner.generate_report()
    
    # Save JSON report if requested
    if args.save_report:
        runner.save_report_json()
    
    # Exit with appropriate code
    exit_code = 0 if overall_success else 1
    
    print(f"\n🏁 Test execution completed with exit code: {exit_code}")
    
    if exit_code == 0:
        print("🎉 All tests passed! System is ready for deployment.")
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
