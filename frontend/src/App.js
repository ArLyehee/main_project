import React, { useEffect, useState } from 'react';

export default function FileManager() {
  const [basePath, setBasePath] = useState('');
  const [filesGrouped, setFilesGrouped] = useState({});
  const [selected, setSelected] = useState(new Set());
  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    fetch(`${API_URL}/api/user/path`)
      .then(r => r.json())
      .then(d => {
        if (d.base_path) {
          setBasePath(d.base_path);
          fetchFiles();
        }
      });
  }, []);

  function savePath() {
    fetch(`${API_URL}/api/user/path`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base_path: basePath })
    })
      .then(r => r.json())
      .then(() => {
        alert('✅ 경로 저장 완료');
        fetchFiles();
      });
  }

  function fetchFiles() {
    fetch(`${API_URL}/api/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
      .then(r => r.json())
      .then(d => {
        setFilesGrouped(d.groupedDocuments || {});
      });
  }

  function toggleSelect(rel) {
    const s = new Set(selected);
    if (s.has(rel)) s.delete(rel);
    else s.add(rel);
    setSelected(s);
  }

  function downloadZip() {
  const filesToZip = Array.from(selected);  // ✅ 선택한 파일만 보내야 함

  if (filesToZip.length === 0) {
    alert('⚠️ 선택된 파일이 없습니다.');
    return;
  }

  fetch(`${API_URL}/api/download-new-zip`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ downloaded_files: filesToZip })  // ✅ 이 값이 선택한 파일만 포함해야 함
  })
    .then(r => r.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'selected_documents.zip';
      a.click();
      window.URL.revokeObjectURL(url);  // 리소스 정리
    });
}

  function downloadAll() {
    fetch(`${API_URL}/api/download-all`, { method: 'POST' })
      .then(r => r.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'all_documents.zip';
        a.click();
        window.URL.revokeObjectURL(url);
      });
  }

  // 폴더 선택 대화상자 (input type="file" with webkitdirectory)
  function openFolderSelector() {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;  // 폴더 선택 가능
    input.directory = true;
    input.multiple = false;
    input.onchange = (e) => {
      if (e.target.files.length > 0) {
        // 첫번째 파일의 경로에서 폴더 경로 추출
        const filePath = e.target.files[0].webkitRelativePath;
        // webkitRelativePath 예: "selected_folder/파일명"
        const baseFolder = filePath.split('/')[0]; 
        // e.target.files[0].path 는 보안상 접근 불가 (브라우저 제한)
        setBasePath(baseFolder);
      }
    };
    input.click();
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>📁 파일 관리 페이지</h2>

      <div style={{ marginBottom: "10px" }}>
        <label>폴더 경로 입력: </label>
                <button onClick={openFolderSelector} style={{ marginLeft: '10px' }}>폴더 선택</button>
        <input
          value={basePath}
          onChange={e => setBasePath(e.target.value)}
          style={{ width: '300px' }}
          placeholder="경로를 입력하거나 폴더 선택"
        />
        <button onClick={savePath} style={{ marginLeft: '10px' }}>저장 & 갱신</button>

      </div>

      <div style={{ marginBottom: '10px' }}>
        <button onClick={downloadAll}>전체 파일 다운로드</button>
        <button onClick={downloadZip} style={{ marginLeft: '10px' }}>선택 파일 다운로드</button>
      </div>

      <div>
        <h3>📄 문서 목록 (카테고리별)</h3>
        {Object.keys(filesGrouped).map(cat => (
          <div key={cat} style={{
            border: '1px solid #ccc', padding: '10px',
            marginBottom: '10px', borderRadius: '8px', backgroundColor: '#fafafa'
          }}>
            <h4>📂 {cat} ({filesGrouped[cat].length})</h4>
            <ul>
              {filesGrouped[cat].map(f => (
                <li key={f.relative_path || f.filename}>
                  {f.relative_path && (
                    <input
                      type="checkbox"
                      onChange={() => toggleSelect(f.relative_path)}
                      checked={selected.has(f.relative_path)}
                    />
                  )}{' '}
                  {f.filename}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
