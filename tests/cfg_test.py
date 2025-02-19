import platform
import unittest
from disassemble_reassemble_check import compile, cd, disassemble
from pathlib import Path
import gtirb


ex_dir = Path("./examples/")
ex_asm_dir = ex_dir / "asm_examples"


class CfgTests(unittest.TestCase):
    @unittest.skipUnless(
        platform.system() == "Linux", "This test is linux only."
    )
    def test_relative_jump_tables(self):
        """
        Test edges for relative jump tables are added.
        """

        binary = "ex"
        with cd(ex_asm_dir / "ex_relative_switch"):
            self.assertTrue(compile("gcc", "g++", "-O0", []))
            self.assertTrue(
                disassemble(
                    binary,
                    "strip",
                    False,
                    False,
                    format="--ir",
                    extension="gtirb",
                )
            )

            ir_library = gtirb.IR.load_protobuf(binary + ".gtirb")
            m = ir_library.modules[0]

            # check that the jumping_block has edges
            # to all the jump table entries
            jumping_block_symbol = [
                s for s in m.symbols if s.name == "jumping_block"
            ][0]
            assert isinstance(jumping_block_symbol.referent, gtirb.CodeBlock)
            jumping_block = jumping_block_symbol.referent
            expected_dest_blocks = [
                s.referent
                for s in m.symbols
                if s.name in ["LBB5_4", "LBB5_5", "LBB5_6", "LBB5_7"]
            ]
            self.assertEqual(len(list(jumping_block.outgoing_edges)), 4)
            dest_blocks = [e.target for e in jumping_block.outgoing_edges]
            self.assertEqual(set(dest_blocks), set(expected_dest_blocks))


if __name__ == "__main__":
    unittest.main()
