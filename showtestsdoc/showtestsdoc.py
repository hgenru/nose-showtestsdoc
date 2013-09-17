import sys
import types
from nose.case import Test
from nose.plugins.base import Plugin
from nose.plugins.collect import TestSuiteFactory

class TestsDoc(Plugin):
    """Plugin to show tests docstring
    """
    name = 'tests_doc'
    enabled = True
    indent = "  "
    indent_count = 1
    latest_context_module_name = ""

    def options(self, parser, env):
        """Register commandline options.
        """
        super(TestsDoc, self).options(parser, env)
        parser.add_option(
            "--tests-doc", action="store_true", dest="tests_doc",
            default=False, help="Show tests docstring.")

    def configure(self, options, conf):
        """Configure plugin.
        """
        super(TestsDoc, self).configure(options, conf)
        self.conf = conf
        self.enabled = bool(options.tests_doc)

    def setOutputStream(self, stream):
        """Get handle on output stream
        """
        self.stream = stream
        class Fake:
            def write(self, *arg):
                pass
            def writeln(self, *arg):
                pass
        return Fake()

    def write(self, output):
        self.stream.write(output)

    def shortenDoc(self, doc):
        return doc and doc.split("\n")[0].strip() or ""

    def writeHr(self, length=70):
        self.write(("-"*length) + "\n")

    def startContext(self, context_suite):
        context_info = {
            "context": context_suite.__name__ or "",
            "doc": self.shortenDoc(context_suite.__doc__)
        }
        formatter = (
            "{context}: {doc}\n"
            )
        if (not isinstance(context_suite, types.ModuleType) \
            and self.latest_context_module_name != context_suite.__module__):
            self.writeHr()
            context_info["module"] = context_suite.__module__
            mod = sys.modules[context_suite.__module__]
            self.write(mod.__name__ + ": " + self.shortenDoc(mod.__doc__) + "\n")
            formatter = self.indent + formatter
            self.latest_context_module_name = context_suite.__module__
            self.indent_count += 1
        elif isinstance(context_suite, types.ModuleType):
            self.indent_count = 2
            if self.latest_context_module_name == context_suite.__name__:
                return
            self.writeHr()
            self.latest_context_module_name = context_suite.__name__
        else:
            self.indent_count = 1
        self.write(formatter.format(**context_info))

    def startTest(self, test_suite):
        test_suite_info = {
            "method": test_suite.address()[2], # filename, context, test
            "doc": test_suite.shortDescription()
        }
        indent = self.indent * self.indent_count
        formatter = (
            indent + "{method}: {doc}\n"
            )
        self.write(formatter.format(**test_suite_info))

    def stopContext(self, context):
        self.writeHr()


    def finalize(self, result):
        self.writeHr()

    def prepareTestLoader(self, loader):
        """Install collect-only suite class in TestLoader.
        """
        # Disable context awareness
        loader.suiteClass = TestSuiteFactory(self.conf)

    def prepareTestCase(self, test):
        """Replace actual test with dummy that always passes.
        """
        # Return something that always passes
        if not isinstance(test, Test):
            return
        def run(result):
            # We need to make these plugin calls because there won't be
            # a result proxy, due to using a stripped-down test suite
            self.conf.plugins.startContext(test.context)
            self.conf.plugins.startTest(test)
            result.startTest(test)
            self.conf.plugins.addSuccess(test)
            result.addSuccess(test)
            self.conf.plugins.stopTest(test)
            result.stopTest(test)
        return run
