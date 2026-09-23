from smart_hospital.model import HospitalModel
from smart_hospital.visualization.dashboard import render_map_snapshot, render_text


def test_render_text_reports_key_fields():
    model = HospitalModel()
    model.spawn_patient(age=40, symptoms="fever", severity=8)
    model.step()
    text = render_text(model)
    assert "Patients waiting" in text
    assert "Doctors available" in text
    assert "ICU beds available" in text


def test_render_map_snapshot_writes_a_file(tmp_path):
    model = HospitalModel()
    model.spawn_patient(age=40, symptoms="fever", severity=8)
    model.step()
    out_path = tmp_path / "snapshot.png"
    render_map_snapshot(model, out_path)
    assert out_path.exists()
    assert out_path.stat().st_size > 0
