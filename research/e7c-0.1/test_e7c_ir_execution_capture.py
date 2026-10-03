import unittest
from unittest.mock import patch

import e7_ir_eecq_two_stage_b1 as ir
from check_e7c_ir_observations import examples, admit_raw_capture, PackageCapture
from e7c_ir_execution_capture import capture_execution, _capture_lock


class CaptureBindingTests(unittest.TestCase):
    def test_actual_parser_inputs_and_complete_native_observations(self):
        # Native serializers are counted; no post-execution reserialization is
        # permitted to provide the captured bytes. Inspect both call sites.
        for source in examples():
            package = ir.lower(source)
            expected = ir.execute(package)
            outer, nested = [], []
            native_outer, native_nested = ir.serialize, ir.serialize_first
            def serialize(value):
                encoded = native_outer(value)
                outer.append(encoded)
                return encoded
            def serialize_first(value):
                encoded = native_nested(value)
                nested.append(encoded)
                return encoded
            with patch.multiple(ir, serialize=serialize, serialize_first=serialize_first):
                capture = capture_execution(package)
            self.assertEqual(capture.result, expected)
            self.assertEqual(len(outer), 1)
            self.assertEqual(len(nested), 1)
            self.assertIs(capture.outer, outer[0])
            self.assertIs(capture.nested, nested[0])
            admit_raw_capture(capture.result, list(capture.transitions))
            receipt = PackageCapture(capture.nested, capture.outer)
            receipt.verify_receipt(receipt.receipt())

    def test_native_exception_produces_no_capture_and_restores_bindings(self):
        before = ir.serialize, ir.parse, ir.serialize_first, ir.parse_first
        with patch.object(ir, "execute", side_effect=RuntimeError("native interruption")):
            with self.assertRaisesRegex(RuntimeError, "native interruption"):
                capture_execution({})
        self.assertEqual(before, (ir.serialize, ir.parse, ir.serialize_first, ir.parse_first))
        self.assertFalse(_capture_lock.locked())

    def test_missing_actual_parse_sites_cannot_claim_binding(self):
        with patch.object(ir, "execute", return_value={}):
            with self.assertRaisesRegex(ValueError, "incomplete"):
                capture_execution({})
        self.assertFalse(_capture_lock.locked())

    def test_equal_bytes_from_a_different_operation_are_rejected(self):
        def forged_execute(package, **kwargs):
            encoded = ir.serialize(package)
            return ir.parse(bytes(bytearray(encoded)))
        source = next(iter(examples()))
        package = ir.lower(source)
        with patch.object(ir, "execute", side_effect=forged_execute):
            with self.assertRaisesRegex(ValueError, "unique serializer return"):
                capture_execution(package)

    def test_repeated_outer_parse_is_rejected(self):
        def repeated(package, **kwargs):
            encoded = ir.serialize(package)
            ir.parse(encoded)
            return ir.parse(encoded)
        package = ir.lower(next(iter(examples())))
        with patch.object(ir, "execute", side_effect=repeated):
            with self.assertRaisesRegex(ValueError, "unique serializer return"):
                capture_execution(package)

    def test_overlapping_capture_refuses_instead_of_rebinding(self):
        _capture_lock.acquire()
        try:
            with self.assertRaisesRegex(ValueError, "overlapping"):
                capture_execution({})
        finally:
            _capture_lock.release()


if __name__ == "__main__":
    unittest.main()
