import os
import tempfile
import shutil
import logging
from cog import BasePredictor, Input, Path
import ffmpeg

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Predictor(BasePredictor):
    def predict(
        self,
        video1: Path = Input(description="Video file to take audio from"),
        video2: Path = Input(description="Video file to apply audio to")
    ) -> Path:
        logger.debug("Starting prediction")
        # Create a temporary directory that persists outside the 'with' block
        tmpdir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {tmpdir}")
        try:
            output_path = os.path.join(tmpdir, "output.mp4")
            logger.debug(f"Output path set to: {output_path}")
            
            # Extract audio from video1
            audio = ffmpeg.input(str(video1)).audio
            logger.debug(f"Extracted audio from: {video1}")
            
            # Get video from video2
            video = ffmpeg.input(str(video2)).video
            logger.debug(f"Extracted video from: {video2}")
            
            # Combine audio from video1 with video from video2
            output = ffmpeg.output(video, audio, output_path)
            logger.debug("Created ffmpeg output object")
            
            # Run the FFmpeg command
            logger.debug("Running FFmpeg command")
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)
            logger.debug("FFmpeg command completed")
            
            if not os.path.exists(output_path):
                logger.error(f"Output file was not created at {output_path}")
                raise FileNotFoundError(f"Output file was not created at {output_path}")
            logger.debug(f"Output file created successfully at {output_path}")
            
            # Create a new path in a directory that Cog expects
            cog_output_dir = Path("/tmp/cog_output")
            cog_output_dir.mkdir(exist_ok=True)
            final_output_path = cog_output_dir / "output.mp4"
            logger.debug(f"Final output path set to: {final_output_path}")
            
            # Copy the file to the new location
            shutil.copy2(output_path, final_output_path)
            logger.debug(f"Copied output file to {final_output_path}")
            
            return final_output_path
        except Exception as e:
            logger.exception("An error occurred during prediction")
            raise
        finally:
            # Clean up the temporary directory
            logger.debug(f"Cleaning up temporary directory: {tmpdir}")
            shutil.rmtree(tmpdir, ignore_errors=True)
