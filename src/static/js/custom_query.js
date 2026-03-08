(function () {
  function readJsonScript(id) {
    var node = document.getElementById(id);
    if (!node || !node.textContent) {
      return null;
    }

    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      console.error('Failed to parse submission JSON from ' + id, error);
      return null;
    }
  }

  function getCsrfToken() {
    var match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  function setSyncStatus(message, isError) {
    var statusEl = document.getElementById('sync-status');
    if (!statusEl) {
      return;
    }
    statusEl.textContent = message;
    statusEl.style.color = isError ? '#b91c1c' : '#1f2937';
  }

  async function createMondayItemsOnBackend() {
    var response = await fetch('/api/monday/create-item/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: '{}'
    });

    if (!response.ok) {
      throw new Error('Backend monday sync HTTP error: ' + response.status);
    }

    var payload = await response.json();
    if (!payload.ok) {
      throw new Error(payload.error || 'Backend monday sync failed.');
    }

    return payload.created_items || {};
  }

  async function runQueryWithSubmissions(businessSubmission, personalSubmission) {
    if (typeof window.runCustomQuery === 'function') {
      await window.runCustomQuery(businessSubmission, personalSubmission);
      return;
    }

    var createdItems = await createMondayItemsOnBackend();
    setSyncStatus('Your submission has been finalized successfully.', false);
    console.log('Created monday items:', createdItems);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var shouldAutoSync = document.body.getAttribute('data-auto-monday-sync') === '1';
    var businessSubmission = readJsonScript('business-submission-data');
    var personalSubmission = readJsonScript('personal-submission-data');

    if (!shouldAutoSync && !businessSubmission && !personalSubmission) {
      return;
    }

    if (shouldAutoSync) {
      setSyncStatus('We are finalizing your submission now.', false);
    }

    runQueryWithSubmissions(businessSubmission, personalSubmission)
      .catch(function (error) {
        setSyncStatus('We could not finalize automatically. Please refresh this page to retry.', true);
        console.error('Post-submit monday sync failed:', error);
      });
  });
})();
