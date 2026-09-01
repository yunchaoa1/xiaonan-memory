import json
from pathlib import Path
import opentimelineio as otio

ROOT = Path(r"D:\Hermes\xiaonan-memory\opc-mvp\03_storyboard_timeline")
SHOTS_PATH = ROOT / "opc_shots.json"
OTIO_PATH = ROOT / "timeline.otio"

package = json.loads(SHOTS_PATH.read_text(encoding="utf-8"))
rate = package["timeline"]["rate"]
shots = package["shots"]

timeline = otio.schema.Timeline(name=package["timeline"]["name"])
timeline.metadata.update({
    "schema": package["schema"],
    "project": package["project"],
    "scope": package["scope"],
    "source_scene_id": package["source"]["scene_id"],
    "shot_count": len(shots),
    "rate": rate,
})
track = otio.schema.Track(name="V1_storyboard", kind=otio.schema.TrackKind.Video)
for shot in shots:
    duration = otio.opentime.RationalTime(shot["duration_seconds"] * rate, rate)
    clip = otio.schema.Clip(
        name=shot["shot_id"],
        media_reference=otio.schema.MissingReference(
            name=f"{shot['shot_id']}_pending_media",
            available_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, rate),
                duration=duration,
            ),
            metadata={"status": "pending_generation"},
        ),
        source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, rate),
            duration=duration,
        ),
        metadata={
            "shot_id": shot["shot_id"],
            "source_scene_id": shot["source_scene_id"],
            "source_node_ids": shot["source_node_ids"],
            "duration_seconds": shot["duration_seconds"],
            "narrative_objective": shot["narrative_objective"],
            "core_action": shot["core_action"],
            "start_state": shot["start_state"],
            "end_state": shot["end_state"],
            "location": shot["location"],
            "opc": shot["metadata"],
        },
    )
    track.append(clip)
timeline.tracks.append(track)
otio.adapters.write_to_file(timeline, str(OTIO_PATH))

# Read back from disk; all checks below use the deserialized object.
loaded = otio.adapters.read_from_file(str(OTIO_PATH))
clips = list(loaded.find_clips())
clip_results = []
for clip in clips:
    seconds = clip.duration().to_seconds()
    clip_results.append({
        "name": clip.name,
        "duration_seconds": seconds,
        "under_or_equal_15": seconds <= 15.0,
        "metadata_shot_id": clip.metadata.get("shot_id"),
        "metadata_scene": clip.metadata.get("source_scene_id"),
        "metadata_node_count": len(clip.metadata.get("source_node_ids", [])),
        "metadata_status": clip.metadata.get("opc", {}).get("status"),
    })

total_seconds = loaded.duration().to_seconds()
expected_total = package["timeline"]["expected_total_seconds"]
assert len(clips) == 3, f"expected 3 clips, got {len(clips)}"
assert all(item["under_or_equal_15"] for item in clip_results)
assert total_seconds == expected_total, (total_seconds, expected_total)
assert loaded.metadata["shot_count"] == 3
assert [c.metadata["shot_id"] for c in clips] == [s["shot_id"] for s in shots]
assert all(c.metadata["opc"]["status"] == "MVP" for c in clips)

print(json.dumps({
    "otio_version": otio.__version__,
    "written": str(OTIO_PATH),
    "readback_timeline": loaded.name,
    "timeline_metadata": dict(loaded.metadata),
    "clips": clip_results,
    "total_seconds": total_seconds,
    "expected_total_seconds": expected_total,
    "validation": "PASS",
}, ensure_ascii=False, indent=2))
