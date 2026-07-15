from app.verify.geographic import score_geographic_consistency, VILLAGE_CENTROIDS


class TestVillageMatch:
    def test_matching_village_scores_well(self, make_input):
        result = score_geographic_consistency(
            make_input(village_at_screening="Wadgaon", asha_assigned_village="Wadgaon", latitude=None, longitude=None)
        )
        assert result.score == 100.0
        assert "village_matches_assignment" in result.flags

    def test_mismatched_village_moderately_deducted_not_zero(self, make_input):
        result = score_geographic_consistency(
            make_input(village_at_screening="Karanjgaon", asha_assigned_village="Wadgaon", latitude=None, longitude=None)
        )
        assert 0 < result.score < 100.0
        assert any(f.startswith("village_mismatch") for f in result.flags)


class TestGpsAvailability:
    def test_missing_gps_defaults_neutral_and_notes_reason(self, make_input):
        result = score_geographic_consistency(
            make_input(village_at_screening="Wadgaon", asha_assigned_village="Wadgaon", latitude=None, longitude=None)
        )
        assert result.available is True  # geographic is never "unavailable" — village check always runs
        assert any(f.startswith("gps_unavailable") for f in result.flags)

    def test_gps_within_service_region_no_deduction(self, make_input):
        lat, lon = VILLAGE_CENTROIDS["Wadgaon"]
        result = score_geographic_consistency(
            make_input(village_at_screening="Wadgaon", asha_assigned_village="Wadgaon",
                       latitude=lat + 0.01, longitude=lon + 0.01)  # ~1km away
        )
        assert result.score == 100.0

    def test_gps_far_outside_service_region_deducted(self, make_input):
        lat, lon = VILLAGE_CENTROIDS["Wadgaon"]
        result = score_geographic_consistency(
            make_input(village_at_screening="Wadgaon", asha_assigned_village="Wadgaon",
                       latitude=lat + 0.5, longitude=lon + 0.5)  # tens of km away
        )
        assert result.score < 100.0
        assert any(f.startswith("outside_service_region") for f in result.flags)
