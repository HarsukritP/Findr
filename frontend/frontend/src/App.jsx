"use client"

import { useState, useEffect } from "react"
import "./App.css"

function App() {
  const [view, setView] = useState("login") // login, register, profile, dashboard, swiping
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [userId, setUserId] = useState(null)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [profiles, setProfiles] = useState([])
  const [userProfile, setUserProfile] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [potentialMatches, setPotentialMatches] = useState([])
  const [matches, setMatches] = useState([])
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0)
  const [pendingMatches, setPendingMatches] = useState([])
  const [showMatches, setShowMatches] = useState(false)
  const [activeTab, setActiveTab] = useState("swipe") // New state for tab management

  // Profile state
  const [profile, setProfile] = useState({
    name: "",
    skills: "",
    experience: "",
    tags: "",
    background: "",
    school: "",
  })

  const [isLoading, setIsLoading] = useState(false)

  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: ""
  });

  const [passwordError, setPasswordError] = useState("");

  // Fetch user's profile
  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`http://localhost:8001/profile/${userId}`)
      const data = await response.json()
      console.log("User Profile Data:", data) // Debug log
      if (response.ok) {
        setUserProfile(data)
        // Pre-fill the edit form
        setProfile({
          name: data.name || "",
          skills: Array.isArray(data.skills) ? data.skills.join(", ") : "",
          experience: Array.isArray(data.experience) ? data.experience.join("\n") : "",
          tags: Array.isArray(data.tags) ? data.tags.join(", ") : "",
          background: data.background || "",
          school: data.school || "",
        })
      } else {
        console.error("Failed to fetch user profile:", data)
      }
    } catch (err) {
      console.error("Error fetching user profile:", err)
    }
  }

  // Fetch all profiles
  const fetchProfiles = async () => {
    try {
      const response = await fetch("http://localhost:8001/profiles")
      const data = await response.json()
      console.log("All Profiles Data:", data) // Debug log
      setProfiles(data)
    } catch (err) {
      console.error("Error fetching profiles:", err)
    }
  }

  // Fetch potential matches
  const fetchPotentialMatches = async () => {
    try {
      const response = await fetch("http://localhost:8001/profiles")
      const data = await response.json()
      console.log("Fetched profiles:", data) // Debug log

      if (!Array.isArray(data)) {
        console.error("Expected array of profiles but got:", data)
        return
      }

      // Filter out the current user's profile and already swiped profiles
      const filteredProfiles = data.filter((profile) => profile._id !== userId)
      console.log("Filtered profiles:", filteredProfiles) // Debug log

      setProfiles(filteredProfiles)
      // Reset the current match index when getting new profiles
      setCurrentMatchIndex(0)
    } catch (error) {
      console.error("Error fetching profiles:", error)
      setError("Failed to fetch potential matches")
    }
  }

  // Fetch matches
  const fetchMatches = async () => {
    try {
      const response = await fetch(`http://localhost:8001/matches/${userId}`)
      const data = await response.json()
      console.log("Fetched matches:", data) // Debug log

      // Transform the data to include user details
      const transformedMatches = data.map((match) => ({
        user: match.matched_user,
        timestamp: match.timestamp,
      }))

      setMatches(transformedMatches)
    } catch (error) {
      console.error("Error fetching matches:", error)
      setError("Failed to fetch matches")
    }
  }

  const fetchPendingMatches = async () => {
    try {
      const response = await fetch(`http://localhost:8001/pending-matches/${userId}`)
      const data = await response.json()
      console.log("Fetched pending matches:", data) // Debug log

      // Transform the data to include user details and type
      const transformedPending = data.map((pending) => ({
        user: pending.user,
        timestamp: pending.timestamp,
        type: pending.type, // Make sure to include the type field
      }))

      setPendingMatches(transformedPending)
    } catch (error) {
      console.error("Error fetching pending matches:", error)
      setError("Failed to fetch pending matches")
    }
  }

  useEffect(() => {
    if (userId && view === "dashboard") {
      console.log("Fetching data for dashboard...") // Debug log
      fetchUserProfile()
      fetchPotentialMatches()
      fetchMatches()
      fetchPendingMatches()
    }
  }, [userId, view])

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (view === "register") {
      if (formData.password !== formData.confirmPassword) {
        setPasswordError("Passwords do not match");
        return;
      }
      if (formData.password.length < 6) {
        setPasswordError("Password must be at least 6 characters long");
        return;
      }
      setPasswordError("");
    }

    try {
      const response = await fetch(`http://localhost:8001/${view === "register" ? 'register' : 'login'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setUserId(data.user_id);
        setMessage(view === "register" ? "Registration successful!" : "Login successful!");
        setError("");
        setView("profile");
      } else {
        setError(data.detail || "An error occurred");
        setMessage("");
      }
    } catch (error) {
      setError("Failed to connect to server");
      setMessage("");
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    try {
      const profileData = {
        name: profile.name,
        skills: profile.skills
          .split(",")
          .map((skill) => skill.trim())
          .filter((skill) => skill),
        experience: profile.experience
          .split("\n")
          .map((exp) => exp.trim())
          .filter((exp) => exp),
        tags: profile.tags
          .split(",")
          .map((tag) => tag.trim())
          .filter((tag) => tag),
        background: profile.background,
        school: profile.school,
      }

      console.log("Submitting profile data:", profileData) // Debug log

      const response = await fetch(`http://localhost:8001/profile/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profileData),
      })

      const data = await response.json()
      console.log("Profile submission response:", data) // Debug log

      if (response.ok) {
        setMessage("Profile updated successfully!")
        setIsEditing(false)
        await fetchUserProfile() // Immediately fetch updated profile
        await fetchPotentialMatches() // Refresh potential matches
        setView("dashboard")
      } else {
        setError(data.detail || "Failed to update profile")
      }
    } catch (err) {
      console.error("Error updating profile:", err)
      setError("Failed to update profile. Please try again.")
    }
  }

  const handleProfileChange = (e) => {
    const { name, value } = e.target
    setProfile((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  // Handle file upload for AI profile generation
  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setIsLoading(true)
    setError(null)
    setMessage(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`http://localhost:8001/analyze-resume/${userId}`, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || "Failed to analyze resume")
      }

      setMessage("Profile created successfully!")
      setView("dashboard")
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Handle swiping
  const handleSwipe = async (liked, specificUserId = null) => {
    // If no specificUserId is provided, we're swiping in discovery mode
    const swipedId = specificUserId || profiles[currentMatchIndex]?._id
    if (!swipedId) return

    try {
      const response = await fetch(`http://localhost:8001/swipe/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          swiped_id: swipedId,
          liked: liked,
        }),
      })

      if (response.ok) {
        if (!specificUserId) {
          // Only increment the index if we're in discovery mode
          setCurrentMatchIndex((prev) => prev + 1)
        }

        // Fetch updated matches and pending matches
        await fetchMatches()
        await fetchPendingMatches()

        const data = await response.json()
        if (data.match_created) {
          setMessage("It's a match! 🎉")
        }
      } else {
        const error = await response.json()
        console.error("Swipe error:", error)
        setError("Failed to record swipe. Please try again.")
      }
    } catch (err) {
      console.error("Swipe error:", err)
      setError("Failed to record swipe. Please try again.")
    }
  }

  const renderMatchCard = () => {
    if (!profiles || profiles.length === 0 || currentMatchIndex >= profiles.length) {
      return (
        <div className="no-matches">
          <h3>No more potential matches available!</h3>
          <p>Check back later for new profiles.</p>
        </div>
      )
    }

    const currentProfile = profiles[currentMatchIndex]
    return (
      <div className="match-card">
        <h2>{currentProfile.name}</h2>
        <p className="school">{currentProfile.school}</p>
        <p className="background">{currentProfile.background}</p>

        <div className="skills-section">
          <h3>Skills</h3>
          <div className="tags-list">
            {currentProfile.skills.map((skill, index) => (
              <span key={index} className="tag skill-tag">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div className="tags-section">
          <h3>Interests</h3>
          <div className="tags-list">
            {currentProfile.tags.map((tag, index) => (
              <span key={index} className="tag interest-tag">
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="experience-section">
          <h3>Experience</h3>
          <ul>
            {currentProfile.experience.map((exp, index) => (
              <li key={index}>{exp}</li>
            ))}
          </ul>
        </div>
      </div>
    )
  }

  const renderMatchesView = () => (
    <div className="matches-view">
      <div className="matches-section">
        <h2>Your Matches</h2>
        {matches.length > 0 ? (
          matches.map((match, index) => (
            <div key={index} className="match-item">
              <h3>{match.user.name}</h3>
              <p className="school">{match.user.school}</p>
              <p className="background">{match.user.background}</p>
              <div className="tags-list">
                {match.user.skills.map((skill, i) => (
                  <span key={i} className="tag skill-tag">
                    {skill}
                  </span>
                ))}
              </div>
              <p className="timestamp">Matched {new Date(match.timestamp).toLocaleDateString()}</p>
            </div>
          ))
        ) : (
          <div className="no-matches">
            <h3>No matches yet</h3>
            <p>Keep swiping to find your perfect teammate!</p>
          </div>
        )}
      </div>

      <div className="pending-matches-section">
        <h2>Pending Matches</h2>
        {pendingMatches.length > 0 ? (
          <>
            <div className="pending-group">
              <h3>People who liked you</h3>
              {pendingMatches
                .filter((match) => match.type === "incoming")
                .map((match, index) => (
                  <div key={index} className="pending-item incoming">
                    <h3>{match.user.name}</h3>
                    <p className="school">{match.user.school}</p>
                    <p className="background">{match.user.background}</p>
                    <div className="tags-list">
                      {match.user.skills.map((skill, i) => (
                        <span key={i} className="tag skill-tag">
                          {skill}
                        </span>
                      ))}
                    </div>
                    <p className="timestamp">
                      Liked you on {new Date(match.timestamp).toLocaleDateString()}
                    </p>
                    <div className="action-buttons">
                      <button
                        className="swipe-button accept"
                        onClick={() => handleSwipe(true, match.user._id)}
                      >
                        Accept
                      </button>
                      <button
                        className="swipe-button reject"
                        onClick={() => handleSwipe(false, match.user._id)}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
            </div>

            <div className="pending-group">
              <h3>People you liked</h3>
              {pendingMatches
                .filter((match) => match.type === "outgoing")
                .map((match, index) => (
                  <div key={index} className="pending-item outgoing">
                    <h3>{match.user.name}</h3>
                    <p className="school">{match.user.school}</p>
                    <p className="background">{match.user.background}</p>
                    <div className="tags-list">
                      {match.user.skills.map((skill, i) => (
                        <span key={i} className="tag skill-tag">
                          {skill}
                        </span>
                      ))}
                    </div>
                    <p className="timestamp">
                      You liked on {new Date(match.timestamp).toLocaleDateString()}
                    </p>
                    <p className="pending-status">Waiting for response</p>
                  </div>
                ))}
            </div>
          </>
        ) : (
          <div className="no-matches">
            <h3>No pending matches</h3>
            <p>Start swiping to find potential teammates!</p>
          </div>
        )}
      </div>
    </div>
  )

  const renderDashboard = () => {
    return (
      <div className="dashboard">
        <div className="dashboard-header">
          <button
            className={`view-toggle ${activeTab === "swipe" ? "active" : ""}`}
            onClick={() => setActiveTab("swipe")}
          >
            Find Matches
          </button>
          <button
            className={`view-toggle ${activeTab === "matches" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("matches")
              fetchMatches()
              fetchPendingMatches()
            }}
          >
            Your Matches
          </button>
        </div>

        {activeTab === "swipe" ? (
          <div className="swiping-container">
            <div className="card-container">{renderMatchCard()}</div>
            <div className="swipe-buttons">
              <button
                className="swipe-button reject"
                onClick={() => handleSwipe(false)}
                disabled={!profiles || profiles.length === 0 || currentMatchIndex >= profiles.length}
              >
                ✗
              </button>
              <button
                className="swipe-button accept"
                onClick={() => handleSwipe(true)}
                disabled={!profiles || profiles.length === 0 || currentMatchIndex >= profiles.length}
              >
                ✓
              </button>
            </div>
          </div>
        ) : (
          renderMatchesView()
        )}
      </div>
    )
  }

  return (
    <div className="app-container">
      <div className="app-content">
        <h1>Findr 🚀</h1>
        <p className="subtitle">Find Your Perfect Hackathon Match!</p>

        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}

        {view === "login" && (
          <div className="auth-form">
            <h2>Welcome Back!</h2>
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>

              <div className="input-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <button type="submit">Login</button>
            </form>

            <div className="toggle-auth-mode">
              <button
                className={!view === "login" ? "active" : ""}
                onClick={() => setView("register")}
              >
                Create Account
              </button>
            </div>
          </div>
        )}

        {view === "register" && (
          <div className="auth-form">
            <h2>Create Account</h2>
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>

              <div className="input-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <div className="input-group">
                <input
                  type="password"
                  placeholder="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  required
                />
                {passwordError && <div className="error">{passwordError}</div>}
              </div>

              <button type="submit">Create Account</button>
            </form>

            <div className="toggle-auth-mode">
              <button
                className={view === "login" ? "active" : ""}
                onClick={() => {
                  setView("login");
                  setFormData({ email: "", password: "", confirmPassword: "" });
                  setPasswordError("");
                }}
              >
                Back to Login
              </button>
            </div>
          </div>
        )}

        {view === "profile" && (
          <div className="profile-form">
            <h2>Upload Your Resume</h2>
            <div className="upload-section">
              <h3>AI-Powered Profile Generation</h3>
              <p>Upload your resume or CV (PDF or Image format)</p>
              <input 
                type="file" 
                accept=".pdf,image/*" 
                onChange={handleFileUpload} 
                className="file-input" 
              />
              {isLoading && (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Analyzing your resume...</p>
                </div>
              )}
            </div>
          </div>
        )}

        {view === "swiping" && (
          <div className="swiping-container">
            <div className="navigation-buttons">
              <button onClick={() => setView("dashboard")}>View Profile</button>
              <button onClick={() => setView("matches")}>View Matches</button>
            </div>

            {profiles.length > currentMatchIndex ? (
              <div className="card-container">
                <div className="profile-card potential-match">
                  <div className="profile-content">
                    <h3>{profiles[currentMatchIndex].name}</h3>
                    <p>
                      <strong>School:</strong> {profiles[currentMatchIndex].school}
                    </p>
                    <p>
                      <strong>Skills:</strong> {profiles[currentMatchIndex].skills.join(", ")}
                    </p>
                    <p>
                      <strong>Experience:</strong>
                    </p>
                    <ul>
                      {profiles[currentMatchIndex].experience.map((exp, index) => (
                        <li key={index}>{exp}</li>
                      ))}
                    </ul>
                    <p>
                      <strong>Tags:</strong> {profiles[currentMatchIndex].tags.join(", ")}
                    </p>
                    <p>
                      <strong>Background:</strong> {profiles[currentMatchIndex].background}
                    </p>
                  </div>
                  <div className="swipe-buttons">
                    <button onClick={() => handleSwipe("left")} className="swipe-left">
                      👎
                    </button>
                    <button onClick={() => handleSwipe("right")} className="swipe-right">
                      👍
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-matches">
                <h3>No more potential matches</h3>
                <p>Check back later for new hackathon teammates!</p>
              </div>
            )}
          </div>
        )}

        {view === "dashboard" && !isEditing && renderDashboard()}

        {view === "matches" && (
          <div className="matches-container">
            <div className="navigation-buttons">
              <button onClick={() => setView("dashboard")}>View Profile</button>
              <button onClick={() => setView("swiping")}>Find Teammates</button>
            </div>
            <h2>Your Matches</h2>
            <div className="matches-grid">
              {matches.map((match) => (
                <div key={match.match_id} className="profile-card match">
                  <div className="profile-content">
                    <h3>{match.user.name}</h3>
                    <p>
                      <strong>School:</strong> {match.user.school}
                    </p>
                    <p>
                      <strong>Skills:</strong> {match.user.skills.join(", ")}
                    </p>
                    <p>
                      <strong>Experience:</strong>
                    </p>
                    <ul>
                      {match.user.experience.map((exp, index) => (
                        <li key={index}>{exp}</li>
                      ))}
                    </ul>
                    <p>
                      <strong>Tags:</strong> {match.user.tags.join(", ")}
                    </p>
                    <p>
                      <strong>Background:</strong> {match.user.background}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

