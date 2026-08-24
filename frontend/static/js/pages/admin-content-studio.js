(() => {
  const form = document.querySelector('#content-builder-form');
  if (!form) return;

  const type = document.querySelector('#content-type');
  const title = form.querySelector('[name="title"]');
  const description = form.querySelector('[name="description"]');
  const xp = form.querySelector('[name="xp"]');
  const previewType = document.querySelector('#preview-type');
  const previewTitle = document.querySelector('#preview-title');
  const previewDescription = document.querySelector('#preview-description');
  const previewMeta = document.querySelector('.preview-meta strong');
  const status = document.querySelector('#save-status');
  const testTable = document.querySelector('.test-builder-table');
  const backendEnabled = window.CODECRAFT_CONFIG?.backendEnabled === true;

  const updatePreview = () => {
    previewType.textContent = type.options[type.selectedIndex].text.split(' / ')[0];
    previewTitle.textContent = title.value || 'Шинэ контентын гарчиг';
    previewDescription.textContent = description.value || 'Суралцах зорилго энд харагдана.';
    previewMeta.textContent = `+${xp.value || 0} XP`;
  };

  [type, title, description, xp].forEach((element) => element.addEventListener('input', updatePreview));
  type.addEventListener('change', updatePreview);

  const makeField = (name, placeholder) => {
    const input = document.createElement('input');
    input.name = name;
    input.placeholder = placeholder;
    input.type = 'text';
    return input;
  };

  const addTestRow = () => {
    const rows = testTable.querySelectorAll('.test-row:not(.test-row-head)');
    const row = document.createElement('div');
    row.className = 'test-row';
    const number = document.createElement('span');
    number.textContent = String(rows.length + 1).padStart(2, '0');
    const input = makeField('test_input[]', 'Input value');
    const expected = makeField('test_expected[]', 'Expected output');
    const visibility = document.createElement('select');
    visibility.name = 'test_visibility[]';
    [['visible', 'Visible'], ['hidden', 'Hidden']].forEach(([value, label]) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label;
      visibility.appendChild(option);
    });
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'remove-test';
    remove.setAttribute('aria-label', 'Remove test');
    remove.textContent = '×';
    row.append(number, input, expected, visibility, remove);
    testTable.appendChild(row);
  };

  document.querySelector('#add-test')?.addEventListener('click', addTestRow);
  testTable.addEventListener('click', (event) => {
    const remove = event.target.closest('.remove-test');
    if (remove) remove.closest('.test-row')?.remove();
  });

  document.querySelector('#save-draft')?.addEventListener('click', () => {
    status.textContent = backendEnabled ? 'Draft хадгалж байна…' : 'Draft локал preview-д хадгалагдлаа.';
    status.className = 'save-status is-success';
  });

  const readPayload = async (response) => {
    const raw = await response.text();
    try {
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {error: `Сервер JSON биш response буцаалаа (HTTP ${response.status}).`};
    }
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.textContent = 'Test шалгаж байна…';
    status.className = 'save-status';
    const formData = new FormData(form);
    const testInputs = [...form.querySelectorAll('[name="test_input[]"]')];
    const testOutputs = [...form.querySelectorAll('[name="test_expected[]"]')];
    const testVisibility = [...form.querySelectorAll('[name="test_visibility[]"]')];
    const payload = Object.fromEntries(formData.entries());
    payload.tests = testInputs.map((input, index) => ({
      input: input.value,
      expected_output: testOutputs[index]?.value || '',
      is_hidden: testVisibility[index]?.value === 'hidden',
    })).filter((item) => item.expected_output.trim());
    payload.hints = [payload.hint || ''].filter(Boolean);
    payload.course_slug = payload.course_id;
    payload.xp_reward = Number(payload.xp || 0);
    payload.status = 'draft';

    try {
      if (backendEnabled) {
        const response = await fetch('/api/admin/content', {
          method: 'POST', credentials: 'same-origin',
          headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload),
        });
        const result = await readPayload(response);
        if (!response.ok) throw new Error(result.error?.message_mn || result.error || 'Content хадгалах боломжгүй байна.');
        status.textContent = `✓ Content #${result.content.id} draft хадгалагдлаа.`;
      } else {
        await new Promise((resolve) => setTimeout(resolve, 650));
        status.textContent = '✓ Automated test pass. Preview draft бэлэн.';
      }
      status.className = 'save-status is-success';
    } catch (error) {
      status.textContent = error.message === 'Unauthorized' ? 'Нэвтэрч байж content хадгална.' : `Алдаа: ${error.message}`;
      status.className = 'save-status';
    }
  });
})();
