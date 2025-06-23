import unittest

from offlinesec_client.icf.yaml_cfg_icf import YamlICFCfg

class TestICFfiles(unittest.TestCase):
    def test_icf_empty_file(self):
        file_name = "..//tests//files/empty.yaml"
        test = YamlICFCfg(file_name=file_name)

        result = len(test.errors)
        error_msg = "Should be one error message. Current value: %s" % (len(test.errors),)
        self.assertEqual(result, 1,  error_msg)

        error_msg = "Should be no warning messages. Current value: %s" % (len(test.warnings),)
        result = len(test.warnings)
        self.assertEqual(result, 0,  error_msg)

if __name__ == '__main__':
    unittest.main()