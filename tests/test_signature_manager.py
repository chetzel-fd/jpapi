#!/usr/bin/env python3
"""Tests for SignatureManager"""

from src.lib.utils.signature_utils import SignatureManager
from datetime import datetime


def test_init():
    """Test initialization"""
    sig_mgr = SignatureManager("testuser")
    assert sig_mgr.user_signature == "testuser"


def test_generate_signature():
    """Test signature generation"""
    sig_mgr = SignatureManager("testuser")
    sig = sig_mgr.generate_signature(include_date=False)
    assert sig == " - testuser"

    sig = sig_mgr.generate_signature(include_date=True)
    today = datetime.now().strftime("%Y.%m.%d")
    assert sig == f" - testuser {today}"


def test_add_signature_to_name():
    """Test adding signature to name"""
    sig_mgr = SignatureManager("testuser")
    name = "Test Policy"
    signed_name = sig_mgr.add_signature_to_name(name, include_date=False)
    assert signed_name == "Test Policy - testuser"

    # Adding signature again should not duplicate it
    signed_again = sig_mgr.add_signature_to_name(signed_name, include_date=False)
    assert signed_again == signed_name


def test_remove_signature_from_name():
    """Test removing signature from name"""
    sig_mgr = SignatureManager("testuser")
    name = "Test Policy - testuser"
    clean_name = sig_mgr.remove_signature_from_name(name)
    assert clean_name == "Test Policy"

    # Name without signature should remain unchanged
    clean_again = sig_mgr.remove_signature_from_name(clean_name)
    assert clean_again == clean_name


def test_update_signature_in_name():
    """Test updating signature in name"""
    sig_mgr = SignatureManager("testuser")
    name = "Test Policy - olduser"
    updated_name = sig_mgr.update_signature_in_name(name, include_date=False)
    assert updated_name == "Test Policy - testuser"
