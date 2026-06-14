"""
API Routes
REST endpoints for scraping job management.
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from auth import token_required
from background_worker import start_job_thread
import uuid
import os
import logging

logger = logging.getLogger(__name__)

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('', methods=['POST'])
@token_required
def create_job(current_user_id, current_username):
    """
    POST /api/jobs
    Create and start a new scraping job.

    Body:
    {
        "hashtags": ["python", "coding"],
        "post_limit": 100,
        "sort_by": "newest"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    hashtags = data.get('hashtags', [])
    post_limit = data.get('post_limit', 50)
    sort_by = data.get('sort_by', 'newest')

    # Validate
    if not hashtags or not isinstance(hashtags, list):
        return jsonify({'error': 'At least one hashtag is required'}), 400

    # Clean hashtags
    hashtags = [h.lstrip('#').strip().lower() for h in hashtags if h.strip()]
    hashtags = list(set(hashtags))  # Remove duplicates

    if not hashtags:
        return jsonify({'error': 'Invalid hashtags provided'}), 400

    if len(hashtags) > 10:
        return jsonify({'error': 'Maximum 10 hashtags allowed'}), 400

    if not isinstance(post_limit, int) or post_limit < 1 or post_limit > 500:
        return jsonify({'error': 'post_limit must be between 1 and 500'}), 400

    if sort_by not in ['newest', 'oldest']:
        return jsonify({'error': 'sort_by must be "newest" or "oldest"'}), 400

    db = current_app.db
    job_uuid = str(uuid.uuid4())

    try:
        job = db.create_job(
            user_id=current_user_id,
            job_uuid=job_uuid,
            hashtags=hashtags,
            post_limit=post_limit,
            sort_by=sort_by
        )

        # Launch background scraping thread
        start_job_thread(
            db=db,
            job_uuid=job_uuid,
            hashtags=hashtags,
            post_limit=post_limit,
            sort_by=sort_by
        )

        logger.info(f"Job {job_uuid} created by user {current_username}")

        return jsonify({
            'message': 'Scraping job started',
            'job_uuid': job_uuid,
            'hashtags': hashtags,
            'post_limit': post_limit,
            'sort_by': sort_by,
            'status': 'pending'
        }), 201

    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        return jsonify({'error': 'Failed to create job'}), 500


@jobs_bp.route('/<job_uuid>', methods=['GET'])
@token_required
def get_job(current_user_id, current_username, job_uuid):
    """
    GET /api/jobs/<job_uuid>
    Get status and details of a specific job.
    """
    db = current_app.db
    job = db.get_job(job_uuid)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'job': job.to_dict()}), 200


@jobs_bp.route('', methods=['GET'])
@token_required
def list_jobs(current_user_id, current_username):
    """
    GET /api/jobs
    List all jobs for the authenticated user.

    FIX: get_user_jobs() now returns dicts directly, so we don't call
    .to_dict() here (which would crash on detached ORM objects).
    """
    db = current_app.db
    jobs = db.get_user_jobs(current_user_id)  # already a list of dicts

    return jsonify({
        'jobs': jobs,
        'total': len(jobs)
    }), 200


@jobs_bp.route('/<job_uuid>/download', methods=['GET'])
@token_required
def download_csv(current_user_id, current_username, job_uuid):
    """
    GET /api/jobs/<job_uuid>/download
    Download the CSV file for a completed job.
    """
    db = current_app.db
    job = db.get_job(job_uuid)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    if job.status != 'completed':
        return jsonify({'error': f'Job is not completed yet (status: {job.status})'}), 400

    if not job.csv_filepath or not os.path.exists(job.csv_filepath):
        return jsonify({'error': 'CSV file not found'}), 404

    return send_file(
        job.csv_filepath,
        mimetype='text/csv',
        as_attachment=True,
        download_name=job.csv_filename
    )


@jobs_bp.route('/<job_uuid>', methods=['DELETE'])
@token_required
def delete_job(current_user_id, current_username, job_uuid):
    """
    DELETE /api/jobs/<job_uuid>
    Cancel or delete a job.
    """
    db = current_app.db
    job = db.get_job(job_uuid)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Delete CSV file if it exists
    if job.csv_filepath and os.path.exists(job.csv_filepath):
        try:
            os.remove(job.csv_filepath)
        except OSError:
            pass

    db.update_job_status(job_uuid=job_uuid, status='cancelled')

    return jsonify({'message': 'Job deleted successfully'}), 200