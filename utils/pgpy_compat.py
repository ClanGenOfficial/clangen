"""
Compatibility layer for pgpy, which brings in heavy cryptography dependencies that
are unnecessary and fail to build for iOS where self-updating is not allowed. 
"""

try:
    import pgpy
except ImportError:
    # On iOS, pgpy will fail to import because we don't install it.
    # Provide a mock so that the consuming code can handle it cleanly.
    
    class MockPGPSignature:
        @classmethod
        def from_blob(cls, *args, **kwargs):
            return None

    class MockPGPKey:
        @classmethod
        def from_file(cls, *args, **kwargs):
            return (None, None)

    class MockErrors:
        class PGPError(Exception):
            pass

    class MockPGPy:
        PGPSignature = MockPGPSignature
        PGPKey = MockPGPKey
        errors = MockErrors()

    pgpy = MockPGPy()
