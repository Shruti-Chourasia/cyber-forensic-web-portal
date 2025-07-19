import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('form');
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showLogin, setShowLogin] = useState(true);
  
  // Login form state
  const [loginData, setLoginData] = useState({
    name: '',
    email: ''
  });
  
  // Form state
  const [formData, setFormData] = useState({
    // Case Information
    case_title: '',
    case_type: 'Civil',
    date_of_submission: '',
    time_of_submission: '',
    investigation_officer: '',
    organization: '',
    contact_number: '',
    email: '',
    
    // Evidence Details (dynamic array)
    evidence_details: [{
      evidence_type: '',
      make_model: '',
      serial_number: '',
      storage_capacity: '',
      quantity: 1,
      condition: 'Working'
    }],
    
    // Description
    description: '',
    
    // Source & Seizure Details
    seized_by: '',
    designation: '',
    place_of_seizure: '',
    seizure_datetime: '',
    authority_of_seizure: '',
    
    // Chain of Custody (dynamic array)
    chain_of_custody: [{
      date_time: '',
      person_handing_over: '',
      person_receiving: '',
      signature_both: '',
      remarks: ''
    }],
    
    // Lab Section
    evidence_received_by: '',
    lab_designation: '',
    receipt_datetime: '',
    assigned_lab_case_id: '',
    initial_assessment: '',
    lab_signature: '',
    receipt_issued: false,
    
    // Declaration
    declaration_signature: '',
    declaration_name: '',
    declaration_designation: '',
    declaration_date: '',
    
    // Terms
    terms_accepted: false
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginData.name || !loginData.email) {
      setMessage('Please enter both name and email');
      return;
    }

    try {
      const response = await axios.post(`${API}/simple-login`, loginData);
      setUser(response.data.user);
      setShowLogin(false);
      setMessage('Login successful!');
    } catch (error) {
      console.error('Login error:', error);
      setMessage('Login failed. Please try again.');
    }
  };

  const handleLogout = () => {
    setUser(null);
    setShowLogin(true);
    setMessage('Logged out successfully');
  };

  const handleLoginInputChange = (e) => {
    const { name, value } = e.target;
    setLoginData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleEvidenceChange = (index, field, value) => {
    const newEvidence = [...formData.evidence_details];
    newEvidence[index][field] = value;
    setFormData(prev => ({ ...prev, evidence_details: newEvidence }));
  };

  const addEvidenceRow = () => {
    setFormData(prev => ({
      ...prev,
      evidence_details: [...prev.evidence_details, {
        evidence_type: '',
        make_model: '',
        serial_number: '',
        storage_capacity: '',
        quantity: 1,
        condition: 'Working'
      }]
    }));
  };

  const removeEvidenceRow = (index) => {
    if (formData.evidence_details.length > 1) {
      const newEvidence = formData.evidence_details.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, evidence_details: newEvidence }));
    }
  };

  const handleCustodyChange = (index, field, value) => {
    const newCustody = [...formData.chain_of_custody];
    newCustody[index][field] = value;
    setFormData(prev => ({ ...prev, chain_of_custody: newCustody }));
  };

  const addCustodyRow = () => {
    setFormData(prev => ({
      ...prev,
      chain_of_custody: [...prev.chain_of_custody, {
        date_time: '',
        person_handing_over: '',
        person_receiving: '',
        signature_both: '',
        remarks: ''
      }]
    }));
  };

  const removeCustodyRow = (index) => {
    if (formData.chain_of_custody.length > 1) {
      const newCustody = formData.chain_of_custody.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, chain_of_custody: newCustody }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.terms_accepted) {
      setMessage('Please accept terms and conditions');
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...formData,
        submitter_email: user?.email || 'anonymous@example.com',
        seizure_datetime: new Date(formData.seizure_datetime).toISOString(),
        receipt_datetime: new Date(formData.receipt_datetime).toISOString(),
        chain_of_custody: formData.chain_of_custody.map(custody => ({
          ...custody,
          date_time: new Date(custody.date_time).toISOString()
        }))
      };

      const response = await axios.post(`${API}/submit-evidence`, submitData);

      setMessage('Evidence submitted successfully! 🎉');
      console.log('Submission successful:', response.data);
      
      // Reset form
      setFormData({
        case_title: '',
        case_type: 'Civil',
        date_of_submission: '',
        time_of_submission: '',
        investigation_officer: '',
        organization: '',
        contact_number: '',
        email: '',
        evidence_details: [{
          evidence_type: '',
          make_model: '',
          serial_number: '',
          storage_capacity: '',
          quantity: 1,
          condition: 'Working'
        }],
        description: '',
        seized_by: '',
        designation: '',
        place_of_seizure: '',
        seizure_datetime: '',
        authority_of_seizure: '',
        chain_of_custody: [{
          date_time: '',
          person_handing_over: '',
          person_receiving: '',
          signature_both: '',
          remarks: ''
        }],
        evidence_received_by: '',
        lab_designation: '',
        receipt_datetime: '',
        assigned_lab_case_id: '',
        initial_assessment: '',
        lab_signature: '',
        receipt_issued: false,
        declaration_signature: '',
        declaration_name: '',
        declaration_designation: '',
        declaration_date: '',
        terms_accepted: false
      });
    } catch (error) {
      console.error('Submission error:', error);
      setMessage('Failed to submit evidence. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    try {
      const response = await axios.get(`${API}/evidence`);
      setSubmissions(response.data.submissions);
    } catch (error) {
      console.error('Error fetching submissions:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'submissions') {
      fetchSubmissions();
    }
  }, [activeTab]);

  if (showLogin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full mx-4">
          <div className="text-center">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">🔒 Cyber Forensic Portal</h1>
              <p className="text-gray-600">Secure Evidence Management System</p>
            </div>
            
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  name="name"
                  value={loginData.name}
                  onChange={handleLoginInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your full name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={loginData.email}
                  onChange={handleLoginInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your email"
                />
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Sign In
              </button>
            </form>
            
            {message && (
              <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg text-blue-700">
                {message}
              </div>
            )}
            
            <div className="mt-6 text-sm text-gray-500">
              <p>🛡️ Simple & Secure Authentication</p>
              <p>📊 Evidence Management System</p>
              <p>🔐 Complete Evidence Tracking</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🔒 Cyber Forensic Portal</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <span className="text-sm font-medium text-gray-700">{user?.name || 'User'}</span>
              </div>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('form')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'form' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📝 Submit Evidence
            </button>
            <button
              onClick={() => setActiveTab('submissions')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'submissions' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📋 View Submissions
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {message && (
          <div className="mb-6 p-4 bg-green-100 border border-green-300 rounded-lg text-green-700">
            {message}
          </div>
        )}

        {activeTab === 'form' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Evidence Submission Form</h2>
              <p className="text-gray-600">Complete all sections for proper evidence tracking</p>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-8">
              {/* Case Information */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Case Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Case Title / Reference No. *
                    </label>
                    <input
                      type="text"
                      name="case_title"
                      value={formData.case_title}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type of Case *
                    </label>
                    <select
                      name="case_type"
                      value={formData.case_type}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Civil">Civil</option>
                      <option value="Criminal">Criminal</option>
                      <option value="Corporate">Corporate</option>
                      <option value="Internal">Internal</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date of Submission *
                    </label>
                    <input
                      type="date"
                      name="date_of_submission"
                      value={formData.date_of_submission}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time of Submission *
                    </label>
                    <input
                      type="time"
                      name="time_of_submission"
                      value={formData.time_of_submission}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Investigation Officer / Client Name *
                    </label>
                    <input
                      type="text"
                      name="investigation_officer"
                      value={formData.investigation_officer}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Organization / Department *
                    </label>
                    <input
                      type="text"
                      name="organization"
                      value={formData.organization}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Contact Number *
                    </label>
                    <input
                      type="tel"
                      name="contact_number"
                      value={formData.contact_number}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email ID *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Evidence Details */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">📦 Evidence Details</h3>
                {formData.evidence_details.map((evidence, index) => (
                  <div key={index} className="mb-4 p-4 bg-white rounded-lg border">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium text-gray-800">Evidence Item {index + 1}</h4>
                      {formData.evidence_details.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeEvidenceRow(index)}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Evidence Type *
                        </label>
                        <input
                          type="text"
                          value={evidence.evidence_type}
                          onChange={(e) => handleEvidenceChange(index, 'evidence_type', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Make/Model *
                        </label>
                        <input
                          type="text"
                          value={evidence.make_model}
                          onChange={(e) => handleEvidenceChange(index, 'make_model', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Serial Number *
                        </label>
                        <input
                          type="text"
                          value={evidence.serial_number}
                          onChange={(e) => handleEvidenceChange(index, 'serial_number', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Storage Capacity
                        </label>
                        <input
                          type="text"
                          value={evidence.storage_capacity}
                          onChange={(e) => handleEvidenceChange(index, 'storage_capacity', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Quantity *
                        </label>
                        <input
                          type="number"
                          value={evidence.quantity}
                          onChange={(e) => handleEvidenceChange(index, 'quantity', parseInt(e.target.value))}
                          required
                          min="1"
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Condition *
                        </label>
                        <select
                          value={evidence.condition}
                          onChange={(e) => handleEvidenceChange(index, 'condition', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="Sealed">Sealed</option>
                          <option value="Damaged">Damaged</option>
                          <option value="Working">Working</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addEvidenceRow}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  + Add Another Evidence Item
                </button>
              </div>

              {/* Description */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">📝 Description of Evidence</h3>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={4}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Provide detailed description of the evidence..."
                />
              </div>

              {/* Source & Seizure Details */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Source & Seizure Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Seized By *
                    </label>
                    <input
                      type="text"
                      name="seized_by"
                      value={formData.seized_by}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Designation *
                    </label>
                    <input
                      type="text"
                      name="designation"
                      value={formData.designation}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Place of Seizure *
                    </label>
                    <input
                      type="text"
                      name="place_of_seizure"
                      value={formData.place_of_seizure}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date/Time of Seizure *
                    </label>
                    <input
                      type="datetime-local"
                      name="seizure_datetime"
                      value={formData.seizure_datetime}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Authority of Seizure (Warrant No.) *
                    </label>
                    <input
                      type="text"
                      name="authority_of_seizure"
                      value={formData.authority_of_seizure}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Chain of Custody */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">🔗 Chain of Custody Log</h3>
                {formData.chain_of_custody.map((custody, index) => (
                  <div key={index} className="mb-4 p-4 bg-white rounded-lg border">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-medium text-gray-800">Custody Record {index + 1}</h4>
                      {formData.chain_of_custody.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeCustodyRow(index)}
                          className="text-red-600 hover:text-red-700 text-sm"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Date & Time *
                        </label>
                        <input
                          type="datetime-local"
                          value={custody.date_time}
                          onChange={(e) => handleCustodyChange(index, 'date_time', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Person Handing Over *
                        </label>
                        <input
                          type="text"
                          value={custody.person_handing_over}
                          onChange={(e) => handleCustodyChange(index, 'person_handing_over', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Person Receiving *
                        </label>
                        <input
                          type="text"
                          value={custody.person_receiving}
                          onChange={(e) => handleCustodyChange(index, 'person_receiving', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Signature (Both) *
                        </label>
                        <input
                          type="text"
                          value={custody.signature_both}
                          onChange={(e) => handleCustodyChange(index, 'signature_both', e.target.value)}
                          required
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Remarks
                        </label>
                        <textarea
                          value={custody.remarks}
                          onChange={(e) => handleCustodyChange(index, 'remarks', e.target.value)}
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addCustodyRow}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  + Add Another Custody Record
                </button>
              </div>

              {/* Lab Section */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">🧪 Cyber Forensic Lab Section (Office Use Only)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Evidence Received By
                    </label>
                    <input
                      type="text"
                      name="evidence_received_by"
                      value={formData.evidence_received_by}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Designation
                    </label>
                    <input
                      type="text"
                      name="lab_designation"
                      value={formData.lab_designation}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date & Time of Receipt
                    </label>
                    <input
                      type="datetime-local"
                      name="receipt_datetime"
                      value={formData.receipt_datetime}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Assigned Lab Case ID
                    </label>
                    <input
                      type="text"
                      name="assigned_lab_case_id"
                      value={formData.assigned_lab_case_id}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Initial Assessment Remarks
                    </label>
                    <textarea
                      name="initial_assessment"
                      value={formData.initial_assessment}
                      onChange={handleInputChange}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Signature (Lab Receiver)
                    </label>
                    <input
                      type="text"
                      name="lab_signature"
                      value={formData.lab_signature}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="receipt_issued"
                      checked={formData.receipt_issued}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-700">
                      Receipt Issued to Submitter
                    </label>
                  </div>
                </div>
              </div>

              {/* Declaration */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">✍️ Declaration by Submitting Authority</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Signature *
                    </label>
                    <input
                      type="text"
                      name="declaration_signature"
                      value={formData.declaration_signature}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      name="declaration_name"
                      value={formData.declaration_name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Designation *
                    </label>
                    <input
                      type="text"
                      name="declaration_designation"
                      value={formData.declaration_designation}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date *
                    </label>
                    <input
                      type="date"
                      name="declaration_date"
                      value={formData.declaration_date}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Terms & Conditions */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Terms & Conditions</h3>
                <div className="bg-white p-4 rounded-lg border max-h-40 overflow-y-auto text-sm text-gray-700">
                  <p className="mb-2"><strong>1. Evidence Integrity:</strong> All submitted evidence must be in original condition and properly sealed.</p>
                  <p className="mb-2"><strong>2. Chain of Custody:</strong> Complete chain of custody must be maintained from seizure to submission.</p>
                  <p className="mb-2"><strong>3. Confidentiality:</strong> All evidence information will be kept confidential and used only for official purposes.</p>
                  <p className="mb-2"><strong>4. Liability:</strong> The submitting authority is responsible for accuracy of provided information.</p>
                  <p className="mb-2"><strong>5. Return Policy:</strong> Evidence will be returned after completion of analysis as per established procedures.</p>
                  <p><strong>6. Legal Compliance:</strong> All procedures comply with applicable laws and regulations.</p>
                </div>
                <div className="mt-4 flex items-center">
                  <input
                    type="checkbox"
                    name="terms_accepted"
                    checked={formData.terms_accepted}
                    onChange={handleInputChange}
                    required
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700">
                    I agree to the terms and conditions *
                  </label>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400"
                >
                  {loading ? 'Submitting...' : 'Submit Evidence Form'}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'submissions' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Evidence Submissions</h2>
              <p className="text-gray-600">View all submitted evidence records</p>
            </div>
            
            <div className="p-6">
              {submissions.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">No evidence submissions found.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {submissions.map((submission, index) => (
                    <div key={submission.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">{submission.case_title}</h3>
                          <p className="text-sm text-gray-600">Case Type: {submission.case_type}</p>
                          <p className="text-sm text-gray-600">Officer: {submission.investigation_officer}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-700">ID: {submission.id}</p>
                          <p className="text-sm text-gray-500">
                            Submitted: {new Date(submission.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3 text-sm">
                        <div>
                          <span className="font-medium">Evidence Items:</span> {submission.evidence_details?.length || 0}
                        </div>
                        <div>
                          <span className="font-medium">Organization:</span> {submission.organization}
                        </div>
                        <div>
                          <span className="font-medium">Lab Case ID:</span> {submission.assigned_lab_case_id || 'Not assigned'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;