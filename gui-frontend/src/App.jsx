import React, { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import './App.css'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'

function App() {
  const [selectedFile, setSelectedFile] = useState('')
  const [availableFiles, setAvailableFiles] = useState([])
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [debug, setDebug] = useState(false)
  const [profile, setProfile] = useState(false)
  const [fileContent, setFileContent] = useState('')
  const [editedContent, setEditedContent] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [compileOutput, setCompileOutput] = useState('')

  // Cargar archivos disponibles al montar
  useEffect(() => {
    loadFiles()
  }, [])

  // Cargar contenido del archivo cuando se selecciona
  useEffect(() => {
    if (selectedFile) {
      loadFileContent(selectedFile)
    }
  }, [selectedFile])

  // Sincronizar editedContent cuando cambia fileContent
  useEffect(() => {
    setEditedContent(fileContent)
  }, [fileContent])

  const loadFiles = async () => {
    try {
      const response = await fetch(`${API_BASE}/files`)
      const data = await response.json()
      if (data.files) {
        setAvailableFiles(data.files)
        if (data.files.length > 0 && !selectedFile) {
          setSelectedFile(data.files[0].path)
        }
      }
    } catch (error) {
      console.error('Error cargando archivos:', error)
    }
  }

  const loadFileContent = async (filePath) => {
    try {
      const response = await fetch(`${API_BASE}/read-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file: filePath })
      })
      const data = await response.json()
      if (data.content) {
        setFileContent(data.content)
      }
    } catch (error) {
      console.error('Error cargando contenido:', error)
    }
  }

  const saveFile = async () => {
    if (!selectedFile) {
      setOutput('Error: No hay archivo seleccionado para guardar')
      return
    }

    try {
      const response = await fetch(`${API_BASE}/save-file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file: selectedFile,
          content: editedContent
        })
      })

      const data = await response.json()
      if (data.success) {
        setFileContent(editedContent)
        setIsEditing(false)
        setOutput('Archivo guardado exitosamente\n')
      } else {
        setOutput(`Error al guardar: ${data.error}\n`)
      }
    } catch (error) {
      setOutput(`Error de conexion: ${error.message}\n`)
    }
  }

  const runCommand = async (action) => {
    // Si hay cambios sin guardar, usar el contenido editado temporalmente
    let fileToUse = selectedFile
    let contentToUse = editedContent

    if (action !== 'repl' && !selectedFile && !contentToUse) {
      setOutput('Error: Por favor selecciona un archivo o escribe codigo primero')
      return
    }

    setLoading(true)
    setOutput('Ejecutando...\n')

    try {
      // Si hay contenido editado diferente, usar endpoint especial
      const endpoint = (isEditing && editedContent !== fileContent && editedContent) 
        ? `${API_BASE}/run-with-content` 
        : `${API_BASE}/run`
      
      const payload = (isEditing && editedContent !== fileContent && editedContent)
        ? {
            action: action,
            content: editedContent,
            debug: debug,
            profile: profile
          }
        : {
            action: action,
            file: fileToUse,
            debug: debug,
            profile: profile
          }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (data.error) {
        setOutput(`Error: ${data.error}\n${data.stderr || ''}`)
        setCompileOutput('')
      } else {
        let result = data.stdout || ''
        if (data.stderr) {
          result += '\n--- Errores ---\n' + data.stderr
        }
        setOutput(result)
        
        // Si hay resultado de compilación, mostrarlo
        if (data.compile_output !== undefined || data.compile_errors !== undefined) {
          let compileInfo = ''
          if (data.compile_success) {
            compileInfo = 'Compilacion exitosa!\n\n'
            
            // Si hay errores de compilación (warnings), mostrarlos
            if (data.compile_errors) {
              compileInfo += 'Advertencias:\n' + data.compile_errors + '\n\n'
            }
            
            // Si hay resultado de ejecución, mostrarlo
            if (data.execution_output !== undefined) {
              compileInfo += '--- Ejecucion del Programa ---\n'
              if (data.execution_success) {
                compileInfo += 'Ejecucion exitosa:\n\n'
              } else {
                compileInfo += 'Error en la ejecucion:\n\n'
              }
              
              if (data.execution_output) {
                compileInfo += data.execution_output
              }
              if (data.execution_errors) {
                compileInfo += data.execution_errors
              }
            }
          } else {
            compileInfo = 'Error en la compilacion:\n\n'
            if (data.compile_output) {
              compileInfo += data.compile_output
            }
            if (data.compile_errors) {
              compileInfo += data.compile_errors
            }
          }
          
          setCompileOutput(compileInfo)
        } else {
          setCompileOutput('')
        }
      }
    } catch (error) {
      setOutput(`Error de conexion: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Compilador B-Minor</h1>
        <p>Interfaz Grafica Educativa</p>
      </header>

      <div className="app-container">
        {/* Panel izquierdo: Seleccion y opciones */}
        <div className="left-panel">
          <div className="card">
            <h2>Archivo</h2>
            <select 
              value={selectedFile} 
              onChange={(e) => setSelectedFile(e.target.value)}
              className="file-select"
            >
              <option value="">-- Selecciona un archivo --</option>
              {availableFiles.map((file, idx) => (
                <option key={idx} value={file.path}>
                  {file.name} ({file.path})
                </option>
              ))}
            </select>
          </div>

          <div className="card">
            <h2>Opciones</h2>
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={debug} 
                onChange={(e) => setDebug(e.target.checked)}
              />
              <span>Modo Debug</span>
            </label>
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={profile} 
                onChange={(e) => setProfile(e.target.checked)}
              />
              <span>Perfilamiento</span>
            </label>
          </div>

          <div className="card">
            <h2>Acciones</h2>
            <div className="button-group">
              <button 
                onClick={() => runCommand('scan')} 
                disabled={loading || !selectedFile}
                className="btn btn-primary"
              >
                Scan
              </button>
              <button 
                onClick={() => runCommand('parse')} 
                disabled={loading || !selectedFile}
                className="btn btn-primary"
              >
                Parse
              </button>
              <button 
                onClick={() => runCommand('check')} 
                disabled={loading || !selectedFile}
                className="btn btn-primary"
              >
                Check
              </button>
              <button 
                onClick={() => runCommand('codegen')} 
                disabled={loading || !selectedFile}
                className="btn btn-success"
              >
                Codegen
              </button>
              <button 
                onClick={() => runCommand('interp')} 
                disabled={loading || !selectedFile}
                className="btn btn-success"
              >
                Interp
              </button>
            </div>
          </div>
        </div>

        {/* Panel derecho: Codigo y salida */}
        <div className="right-panel">
          <div className="card">
            <div className="editor-header">
              <h2>Editor de Codigo</h2>
              <div className="editor-actions">
                {isEditing && editedContent !== fileContent && (
                  <span className="unsaved-badge">● Sin guardar</span>
                )}
                {!isEditing ? (
                  <button 
                    onClick={() => setIsEditing(true)}
                    className="btn btn-secondary btn-small"
                  >
                    Editar
                  </button>
                ) : (
                  <>
                    <button 
                      onClick={saveFile}
                      className="btn btn-success btn-small"
                    >
                      Guardar
                    </button>
                    <button 
                      onClick={() => {
                        setEditedContent(fileContent)
                        setIsEditing(false)
                      }}
                      className="btn btn-secondary btn-small"
                    >
                      Cancelar
                    </button>
                  </>
                )}
              </div>
            </div>
            <div className="editor-container">
              <Editor
                height="400px"
                defaultLanguage="c"
                value={editedContent}
                onChange={(value) => {
                  setEditedContent(value || '')
                  if (!isEditing) setIsEditing(true)
                }}
                theme="vs-dark"
                options={{
                  minimap: { enabled: true },
                  fontSize: 14,
                  wordWrap: 'on',
                  automaticLayout: true,
                  scrollBeyondLastLine: false,
                  readOnly: !isEditing
                }}
              />
            </div>
            {!selectedFile && (
              <div className="editor-hint">
                Escribe codigo B-Minor aqui o selecciona un archivo arriba
              </div>
            )}
          </div>

          <div className="card">
            <h2>Salida</h2>
            <div className="output-container">
              {loading ? (
                <div className="loading">Procesando...</div>
              ) : (
                <pre className="output">{output || 'La salida aparecera aqui...'}</pre>
              )}
            </div>
            <button 
              onClick={() => {
                setOutput('')
                setCompileOutput('')
              }} 
              className="btn btn-secondary btn-small"
            >
              Limpiar
            </button>
          </div>

          {compileOutput && (
            <div className="card">
              <h2>Resultado de Compilacion LLVM</h2>
              <div className="output-container">
                <pre className="output">{compileOutput}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

