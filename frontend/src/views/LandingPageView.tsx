import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  ArrowRight, 
  Globe, 
  Cpu, 
  Database, 
  Layers, 
  Droplets, 
  Activity, 
  ShieldCheck, 
  ChevronRight,
  Home,
  Info,
  Wrench,
  LineChart,
  LayoutDashboard,
  Sprout,
  MapPin,
  FileSpreadsheet
} from 'lucide-react';
import { GradientWaves } from '../components/reactbits/GradientWaves';
import { GlareHover } from '../components/reactbits/GlareHover';
import { Dock } from '../components/reactbits/Dock';

interface LandingPageViewProps {
  onEnterDashboard: (tabId?: string) => void;
}

export const LandingPageView: React.FC<LandingPageViewProps> = ({ onEnterDashboard }) => {
  const [activeSection, setActiveSection] = useState('home');

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        let maxIntersectionRatio = 0;
        let visibleSection = activeSection;

        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio > maxIntersectionRatio) {
            maxIntersectionRatio = entry.intersectionRatio;
            visibleSection = entry.target.id;
          }
        });

        if (maxIntersectionRatio > 0) {
          setActiveSection(visibleSection);
        }
      },
      {
        root: null,
        rootMargin: '-20% 0px -60% 0px',
        threshold: [0, 0.1, 0.2, 0.5, 0.8, 1.0],
      }
    );

    const sections = ['home', 'about', 'how-it-works', 'modules', 'technology', 'intelligence'];
    sections.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [activeSection]);

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const dockItems = [
    { id: 'home', label: 'Home', icon: <Home className="w-5 h-5" />, onClick: () => scrollTo('home') },
    { id: 'about', label: 'About', icon: <Info className="w-5 h-5" />, onClick: () => scrollTo('about') },
    { id: 'how-it-works', label: 'System', icon: <Activity className="w-5 h-5" />, onClick: () => scrollTo('how-it-works') },
    { id: 'modules', label: 'Platform', icon: <Layers className="w-5 h-5" />, onClick: () => scrollTo('modules') },
    { id: 'technology', label: 'Technology', icon: <Wrench className="w-5 h-5" />, onClick: () => scrollTo('technology') },
    { id: 'intelligence', label: 'Insights', icon: <LineChart className="w-5 h-5" />, onClick: () => scrollTo('intelligence') },
  ];

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 font-sans overflow-x-hidden selection:bg-emerald-500 selection:text-slate-950 scroll-smooth">
      
      {/* 
        =================
        FLOATING DOCK NAV 
        =================
      */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <Dock items={dockItems} activeId={activeSection} />
      </div>

      {/* 
        =================
        HEADER 
        =================
      */}
      <header className="fixed top-0 left-0 right-0 h-20 border-b border-slate-800/80 bg-[#070b14]/85 backdrop-blur-md z-40 transition-all duration-300 shadow-lg shadow-black/30">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => scrollTo('home')}>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shadow-md shadow-emerald-500/20">
              <Bot className="w-6 h-6 text-emerald-400" />
            </div>
            <div className="hidden sm:flex items-center space-x-2">
              <span className="text-lg font-black tracking-wider text-white">PRECISION</span>
              <span className="text-[10px] font-mono font-bold tracking-widest text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-2 py-0.5 rounded-md">
                SERICULTURE AI
              </span>
            </div>
          </div>

          <div className="hidden lg:flex items-center space-x-8 text-sm font-medium text-slate-400">
            <span onClick={() => scrollTo('home')} className={`cursor-pointer transition-colors ${activeSection === 'home' ? 'text-emerald-400 font-bold' : 'hover:text-emerald-400'}`}>Home</span>
            <span onClick={() => scrollTo('about')} className={`cursor-pointer transition-colors ${activeSection === 'about' ? 'text-emerald-400 font-bold' : 'hover:text-emerald-400'}`}>About</span>
            <span onClick={() => scrollTo('how-it-works')} className={`cursor-pointer transition-colors ${activeSection === 'how-it-works' ? 'text-emerald-400 font-bold' : 'hover:text-emerald-400'}`}>How It Works</span>
            <span onClick={() => scrollTo('modules')} className={`cursor-pointer transition-colors ${activeSection === 'modules' ? 'text-emerald-400 font-bold' : 'hover:text-emerald-400'}`}>Platform</span>
            <span onClick={() => scrollTo('technology')} className={`cursor-pointer transition-colors ${activeSection === 'technology' ? 'text-emerald-400 font-bold' : 'hover:text-emerald-400'}`}>Technology</span>
          </div>

          <button 
            onClick={() => onEnterDashboard()}
            className="flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-md shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer"
          >
            <LayoutDashboard className="w-4 h-4 text-slate-950" />
            <span>Live Dashboard</span>
            <ArrowRight className="w-3.5 h-3.5 text-slate-950" />
          </button>
        </div>
      </header>

      {/* 
        =================
        HERO SECTION (Video + Sericulture Emerald GradientWaves)
        =================
      */}
      <section id="home" className="relative min-h-[100vh] flex items-center justify-center pt-20 overflow-hidden bg-[#070b14]">
        
        {/* Layer 1: Background Video */}
        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover object-center opacity-45 scale-105 filter brightness-75 contrast-125"
          >
            <source src="/168572-839370257.mp4" type="video/mp4" />
          </video>
        </div>

        {/* Layer 2: Sericulture Emerald Gradient Waves */}
        <div className="absolute inset-0 z-10 pointer-events-auto overflow-hidden opacity-60 mix-blend-screen">
          <GradientWaves 
            horizonColor="#059669"
            waveColor="#042f2e"
            crestColor="#34d399"
            speed={0.3}
            amplitude={2.0}
            waveScale={0.55}
            waveRatio={0.9}
            swell={28}
            turbulence={16}
            tilt={1.12}
            zoom={1.05}
            height={5.5}
            fogDepth={16}
            detail="medium"
            brightness={1.05}
            opacity={0.75}
            mouseInteraction={true}
            parallaxStrength={0.4}
            grain={true}
            grainIntensity={0.03}
            className="w-full h-full"
          />
        </div>

        {/* Layer 3: Dark Sericulture Gradient Scrim for Contrast */}
        <div className="absolute inset-0 z-10 bg-gradient-to-b from-[#070b14]/85 via-[#070b14]/65 to-[#070b14] pointer-events-none" />

        {/* Hero Content */}
        <div className="relative z-20 max-w-5xl mx-auto px-6 text-center flex flex-col items-center mt-[-4vh]">
          
          {/* Badge from photo style */}
          <div className="inline-flex items-center space-x-2 bg-emerald-950/80 backdrop-blur-md border border-emerald-500/40 text-emerald-400 px-4 py-1.5 rounded-full text-xs font-mono mb-8 font-semibold shadow-lg shadow-emerald-950/40">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>4WD Autonomous Rover • Rack-and-Pinion Probing Active</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white mb-6 leading-tight drop-shadow-lg">
            Precision Intelligence for <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
              Every Mulberry Field
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed drop-shadow">
            Real-time <em>Morus alba</em> agronomy pipeline: automated Modbus RTU RS485 soil probing, spatial neural network interpolation, and targeted fertilizer deficit calculation.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <button 
              onClick={() => onEnterDashboard()}
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-gradient-to-r from-emerald-400 via-emerald-500 to-teal-500 hover:from-emerald-300 hover:via-emerald-400 hover:to-teal-400 text-slate-950 font-black text-lg flex items-center justify-center space-x-3 transition-all duration-300 shadow-xl shadow-emerald-950/60 hover:shadow-2xl hover:shadow-emerald-500/30 hover:scale-[1.03] active:scale-[0.98] cursor-pointer group"
            >
              <LayoutDashboard className="w-5 h-5 text-slate-950" />
              <span>Launch Live Dashboard</span>
              <ArrowRight className="w-5 h-5 text-slate-950 group-hover:translate-x-1 transition-transform" />
            </button>

            <button 
              onClick={() => scrollTo('how-it-works')} 
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 hover:border-emerald-500/50 text-slate-200 hover:text-white font-semibold text-lg flex items-center justify-center space-x-2 transition-all shadow-lg shadow-black/40 hover:shadow-xl backdrop-blur-md cursor-pointer group"
            >
              <span>How It Works</span>
              <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
            </button>
          </div>
        </div>

        {/* Bottom Fade Mask into next section */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#070b14] to-transparent pointer-events-none z-20" />
      </section>

      {/* 
        =================
        ABOUT SECTION 
        =================
      */}
      <section id="about" className="py-24 relative bg-[#070b14] border-t border-slate-800/80">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="inline-flex items-center space-x-2 text-emerald-400 font-mono text-sm mb-6 font-semibold">
            <Info className="w-4 h-4" />
            <span>THE CHALLENGE</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-black text-white mb-6 leading-tight">
            Why Automate Soil Intelligence?
          </h2>
          <p className="text-slate-300 text-lg md:text-xl leading-relaxed mb-8">
            Traditional sericulture relies on manual soil sampling, resulting in sparse data and inaccurate nutrient prescriptions. This leads to over-fertilization, increased costs, and compromised mulberry leaf quality—the primary food source for silkworms.
          </p>
          <div className="p-6 rounded-2xl bg-[#0d1627]/90 border border-emerald-500/20 inline-block text-left shadow-xl shadow-black/30">
            <h4 className="text-emerald-400 font-bold mb-2 text-base flex items-center space-x-2">
              <Sprout className="w-5 h-5 text-emerald-400" />
              <span>The Solution</span>
            </h4>
            <p className="text-slate-300 text-sm max-w-lg leading-relaxed">
              Mulberry automates the entire sampling lifecycle. Our 4WD rover autonomously navigates fields, probing the soil at optimal GPS coordinates. This dense dataset is processed using spatial interpolation (IDW/EfficientNet) to map exact nutrient deficits.
            </p>
          </div>
        </div>
      </section>

      {/* 
        =================
        HOW IT WORKS 
        =================
      */}
      <section id="how-it-works" className="py-24 relative bg-[#090e1a] border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-black text-white mb-4">The Autonomous Pipeline</h2>
            <p className="text-slate-400 max-w-2xl mx-auto text-lg">From physical field probing to spatial interpolation and actionable nutrient prescriptions.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6 relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-emerald-500/0 via-emerald-500/30 to-emerald-500/0 -translate-y-1/2 z-0" />

            {[
              { icon: Bot, title: "Autonomous Rover", desc: "4WD robotic platform navigates to specific GPS waypoints in the field." },
              { icon: Activity, title: "Soil Sensing", desc: "Rack-and-pinion deploys NPK/pH/EC sensors via Modbus RS485." },
              { icon: Cpu, title: "Spatial ML", desc: "FastAPI backend runs EfficientNet & IDW for spatial field interpolation." },
              { icon: Droplets, title: "Agronomic Insights", desc: "Actionable prescription maps generated for targeted fertilizer dosing." }
            ].map((step, idx) => (
              <GlareHover key={idx} className="relative z-10 h-full w-full rounded-2xl" scale={1.03}>
                <div className="h-full bg-[#0d1627]/90 border border-slate-800/90 p-8 rounded-2xl flex flex-col items-center text-center group shadow-lg hover:border-emerald-500/50 hover:shadow-emerald-950/20 transition-all">
                  <div className="w-16 h-16 rounded-2xl bg-emerald-950/50 border border-emerald-500/30 flex items-center justify-center mb-6 group-hover:border-emerald-400 group-hover:bg-emerald-900/60 transition-colors">
                    <step.icon className="w-8 h-8 text-emerald-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{step.desc}</p>
                </div>
              </GlareHover>
            ))}
          </div>
        </div>
      </section>

      {/* 
        =================
        PLATFORM MODULES
        =================
      */}
      <section id="modules" className="py-24 relative bg-[#070b14] border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-black text-white mb-4">Explore the Mulberry Platform</h2>
            <p className="text-slate-400 max-w-2xl mx-auto text-lg">One platform for rover operations, soil intelligence, and agronomic decisions.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { id: 'overview', icon: LayoutDashboard, title: "Dashboard", desc: "Central overview of rover activity, soil metrics, and field intelligence." },
              { id: 'rover', icon: Bot, title: "Rover Telemetry & State", desc: "Monitor rover state, telemetry, and probing operations." },
              { id: 'agronomy', icon: Sprout, title: "Mulberry Agronomy", desc: "Explore agronomic conditions and field-level insights." },
              { id: 'spatial', icon: MapPin, title: "Spatial ML Predictions", desc: "Visualize spatial prediction outputs across the field." },
              { id: 'prescriptions', icon: FileSpreadsheet, title: "Fertilizer Prescriptions", desc: "Turn soil intelligence into targeted fertilizer recommendations." },
              { id: 'samples', icon: Database, title: "Soil Observations", desc: "Review collected soil measurements and observations." }
            ].map((mod) => (
              <GlareHover key={mod.id} className="h-full w-full rounded-2xl" scale={1.02}>
                <div 
                  onClick={() => onEnterDashboard(mod.id)}
                  className="h-full cursor-pointer bg-[#0d1627]/90 p-8 rounded-2xl border border-slate-800/90 hover:border-emerald-500/50 flex flex-col items-start text-left group transition-all duration-300 relative overflow-hidden shadow-lg hover:shadow-2xl hover:shadow-emerald-950/30"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-teal-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10 w-12 h-12 rounded-xl bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center mb-6 group-hover:bg-emerald-500 group-hover:text-slate-950 transition-all">
                    <mod.icon className="w-6 h-6 text-emerald-400 group-hover:text-slate-950 transition-colors" />
                  </div>
                  
                  <h3 className="relative z-10 text-xl font-bold text-white mb-3 group-hover:text-emerald-400 transition-colors">{mod.title}</h3>
                  <p className="relative z-10 text-sm text-slate-400 mb-6 flex-1 leading-relaxed">{mod.desc}</p>
                  
                  <div className="relative z-10 flex items-center space-x-2 text-xs font-bold tracking-wider text-emerald-400 opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300">
                    <span>LAUNCH MODULE</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </GlareHover>
            ))}
          </div>
        </div>
      </section>

      {/* 
        =================
        TECHNOLOGY SECTION 
        =================
      */}
      <section id="technology" className="py-24 relative bg-[#090e1a] border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            
            <div>
              <div className="inline-flex items-center space-x-2 text-emerald-400 font-mono text-sm mb-6 font-semibold">
                <Database className="w-4 h-4" />
                <span>TECH STACK & ARCHITECTURE</span>
              </div>
              <h2 className="text-3xl md:text-5xl font-black text-white mb-6 leading-tight">
                Engineered for <br/>
                <span className="text-emerald-400">Field Accuracy</span>
              </h2>
              <p className="text-slate-300 text-lg mb-8 leading-relaxed">
                The Mulberry platform is built on a robust architecture spanning edge microcontrollers to advanced deep learning models. 
                We process raw Modbus telemetry through a modern FastAPI backend to generate precise spatial agronomic maps.
              </p>
              
              <div className="space-y-6">
                {[
                  { title: "ESP32 & ROS 2", desc: "Real-time edge control and micro-ROS telemetry publishing." },
                  { title: "Inverse Distance Weighting (IDW)", desc: "Baseline spatial interpolation for field nutrient gradients." },
                  { title: "EfficientNet Regressor", desc: "Advanced spatial feature extraction for complex field topography." },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start space-x-4">
                    <div className="mt-1 w-6 h-6 rounded-full bg-emerald-950 border border-emerald-500/40 flex items-center justify-center shrink-0">
                      <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    </div>
                    <div>
                      <h4 className="text-white font-bold mb-1">{item.title}</h4>
                      <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 blur-3xl opacity-40 pointer-events-none rounded-[3rem]" />
              <div className="relative bg-[#060a12] p-6 rounded-3xl border border-slate-800 shadow-2xl">
                {/* Simulated Code/Tech visual */}
                <div className="bg-[#03060c] rounded-2xl border border-slate-800/80 p-4 font-mono text-xs sm:text-sm overflow-hidden text-slate-400 h-[400px] flex flex-col">
                  <div className="flex space-x-2 mb-4 pb-4 border-b border-slate-800">
                    <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                    <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  </div>
                  <div className="flex-1 overflow-y-auto opacity-80 select-none">
                    <p className="text-emerald-400 mb-2"># FastAPI Telemetry Ingestion</p>
                    <p><span className="text-pink-400">@app.post</span>(<span className="text-amber-300">"/api/telemetry"</span>)</p>
                    <p><span className="text-purple-400">async def</span> <span className="text-blue-400">ingest_telemetry</span>(telemetry: TelemetryModel):</p>
                    <p className="ml-4">logger.info(<span className="text-amber-300">f"Received payload from WP: {'{telemetry.waypoint_id}'}"</span>)</p>
                    <p className="ml-4">db.insert(telemetry)</p>
                    <p className="ml-4 text-emerald-400"># Trigger inference pipeline</p>
                    <p className="ml-4">features = extract_spatial_features(telemetry)</p>
                    <p className="ml-4">prediction = efficientnet_model.predict(features)</p>
                    <br/>
                    <p className="text-emerald-400 mb-2"># State Machine Step</p>
                    <p><span className="text-purple-400">def</span> <span className="text-blue-400">step</span>(self):</p>
                    <p className="ml-4"><span className="text-purple-400">if</span> self.state == <span className="text-amber-300">"DEPLOYMENT"</span>:</p>
                    <p className="ml-8">self.rack_pinion.lower()</p>
                    <p className="ml-8">self.modbus.read_holding_registers()</p>
                    <p className="ml-4 text-slate-500">...</p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 
        =================
        SOIL INTELLIGENCE SECTION (Directly matching Dashboard KPIs)
        =================
      */}
      <section id="intelligence" className="py-24 relative bg-[#070b14] border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="inline-flex items-center space-x-2 text-emerald-400 font-mono text-sm mb-6 font-semibold">
            <Globe className="w-4 h-4" />
            <span>ACTIONABLE DATA</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Deep Soil Intelligence</h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-lg mb-16">
            Mulberry converts raw telemetry into visual, actionable health metrics. Monitor pH, moisture, electrical conductivity, and N-P-K levels across your entire plantation.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto text-left">
            
            {/* Stat Card 1: Total Probed Samples */}
            <div className="bg-[#0d1627]/90 p-6 rounded-2xl border border-slate-800/90 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">TOTAL PROBED SAMPLES</span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <Database className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-4xl font-black text-white mb-2">48</div>
              </div>
              <div className="flex items-center justify-between text-xs pt-4 border-t border-slate-800/60 text-slate-400">
                <span>Across 6 Plantation Missions</span>
                <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-mono font-semibold">+12 this mission</span>
              </div>
            </div>

            {/* Stat Card 2: Average Soil pH */}
            <div className="bg-[#0d1627]/90 p-6 rounded-2xl border border-slate-800/90 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">AVERAGE SOIL PH</span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <Activity className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-4xl font-black text-white mb-2">6.82 <span className="text-lg font-normal text-slate-400">pH</span></div>
              </div>
              <div className="flex items-center justify-between text-xs pt-4 border-t border-slate-800/60 text-slate-400">
                <span>Target: 6.5 – 7.5 pH</span>
                <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">OPTIMAL</span>
              </div>
            </div>

            {/* Stat Card 3: Electrical Conductivity */}
            <div className="bg-[#0d1627]/90 p-6 rounded-2xl border border-slate-800/90 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">ELECTRICAL CONDUCTIVITY</span>
                  <div className="w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                    <Activity className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-4xl font-black text-white mb-2">0.74 <span className="text-lg font-normal text-slate-400">dS/m</span></div>
              </div>
              <div className="flex items-center justify-between text-xs pt-4 border-t border-slate-800/60 text-slate-400">
                <span>Target: &lt; 1.0 dS/m</span>
                <span className="bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-bold">NORMAL</span>
              </div>
            </div>

            {/* Stat Card 4: Total NPK Shortfall */}
            <div className="bg-[#0d1627]/90 p-6 rounded-2xl border border-slate-800/90 shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-slate-400 text-xs font-bold uppercase tracking-wider">TOTAL N-P-K SHORTFALL</span>
                  <div className="w-8 h-8 rounded-lg bg-rose-950/60 border border-rose-500/30 flex items-center justify-center text-rose-400">
                    <Droplets className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-4xl font-black text-white mb-2">4,081 <span className="text-lg font-normal text-slate-400">kg/ha</span></div>
              </div>
              <div className="flex items-center justify-between text-xs pt-4 border-t border-slate-800/60 text-slate-400">
                <span>Mulberry Plantation Deficit</span>
                <span className="bg-rose-950/80 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded font-bold text-[10px]">REQUIRES DOSING</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 
        =================
        DASHBOARD CTA PREVIEW 
        =================
      */}
      <section className="py-24 relative bg-[#090e1a] border-t border-slate-800/80 overflow-hidden pb-48">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-emerald-950/20 via-[#090e1a] to-[#090e1a] pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-6 relative z-10 flex flex-col items-center text-center">
          <h2 className="text-3xl md:text-5xl font-black text-white mb-6">From Field Data to Actionable Intelligence</h2>
          <p className="text-slate-400 text-lg mb-12 max-w-xl">
            Access the Precision Sericulture Dashboard to monitor rover telemetry, view spatial ML heatmaps, and generate targeted fertilizer prescriptions.
          </p>

          <GlareHover scale={1.02} className="w-full max-w-4xl rounded-[2.5rem]">
            <div 
              onClick={() => onEnterDashboard()}
              className="cursor-pointer group relative rounded-[2.5rem] p-2 bg-gradient-to-b from-slate-800 to-slate-950 shadow-2xl shadow-emerald-950/40 border border-slate-800 overflow-hidden"
            >
              {/* Simulated Dashboard UI Frame */}
              <div className="bg-[#060a12] rounded-[2rem] border border-slate-800/80 h-auto min-h-[460px] overflow-hidden relative">
                
                <div className="absolute inset-0 flex items-center justify-center z-20 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-xs">
                  <div className="px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-full flex items-center space-x-3 transform translate-y-4 group-hover:translate-y-0 transition-transform shadow-xl shadow-emerald-500/25">
                    <span>Explore Live Dashboard &rarr;</span>
                  </div>
                </div>

                <div className="h-14 border-b border-slate-800 flex items-center px-6 justify-between bg-[#0b1322]/80">
                  <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm tracking-wide">
                    <LayoutDashboard className="w-4 h-4" />
                    <span>DASHBOARD OVERVIEW</span>
                  </div>
                  <div className="flex space-x-3">
                    <div className="text-xs font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-500/30 px-3 py-1 rounded-full flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      <span>SYSTEM LIVE</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 grid grid-cols-1 md:grid-cols-4 gap-6 text-left">
                  <div className="md:col-span-3 space-y-6">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-[#0d1627] border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">Total Samples</div>
                        <div className="text-2xl font-black text-white">1,248</div>
                      </div>
                      <div className="bg-[#0d1627] border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">Avg Soil pH</div>
                        <div className="text-2xl font-black text-emerald-400">6.82</div>
                      </div>
                      <div className="bg-[#0d1627] border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">N-P-K Status</div>
                        <div className="text-2xl font-black text-teal-400">Optimal</div>
                      </div>
                    </div>
                    <div className="h-44 bg-[#0d1627] border border-slate-800 rounded-2xl p-4 flex flex-col justify-between">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-slate-300 font-semibold text-sm">Moisture Trend (7 Days)</span>
                        <span className="text-emerald-400 text-xs font-bold bg-emerald-500/10 px-2 py-1 rounded">+2.4%</span>
                      </div>
                      <div className="flex items-end justify-between h-full pt-4 space-x-2">
                        {[40, 55, 45, 70, 65, 80, 75].map((h, i) => (
                          <div key={i} style={{ height: `${h}%` }} className="w-full bg-emerald-500/30 hover:bg-emerald-500/50 transition-colors rounded-t-sm relative group">
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 text-xs text-white bg-slate-800 px-2 rounded transition-opacity">
                              {h}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-6">
                    <div className="bg-[#0d1627] border border-slate-800 rounded-2xl p-4">
                      <div className="text-slate-400 text-xs font-semibold mb-3 uppercase">Rover State</div>
                      <div className="flex items-center space-x-3 mb-2">
                        <Bot className="w-8 h-8 text-emerald-400" />
                        <div>
                          <div className="text-white font-bold text-sm">INTERROGATION</div>
                          <div className="text-slate-400 text-xs">Battery: 98%</div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-[#0d1627] border border-slate-800 rounded-2xl p-4 space-y-4">
                      <div className="text-slate-400 text-xs font-semibold uppercase">Latest Anomalies</div>
                      {[
                        { label: 'Low Phosphorus', zone: 'Zone A', color: 'text-rose-400' },
                        { label: 'Moisture Drop', zone: 'Zone C', color: 'text-amber-400' },
                        { label: 'pH Imbalance', zone: 'Zone B', color: 'text-amber-400' }
                      ].map((item, i) => (
                         <div key={i} className="flex justify-between items-center text-sm border-b border-slate-800/50 pb-2 last:border-0 last:pb-0">
                           <span className={item.color}>{item.label}</span>
                           <span className="text-slate-500 text-xs">{item.zone}</span>
                         </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </GlareHover>
        </div>
      </section>

      {/* 
        =================
        FOOTER 
        =================
      */}
      <footer className="border-t border-slate-800/80 bg-[#050810] py-12 pb-32">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-sm text-slate-500">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Bot className="w-5 h-5 text-emerald-400 opacity-90" />
            <span className="text-slate-400 font-medium">© 2026 Mulberry Precision Sericulture Project</span>
          </div>
          <div className="flex items-center space-x-6">
            <span className="hover:text-emerald-400 cursor-pointer transition-colors">Documentation</span>
            <span className="hover:text-emerald-400 cursor-pointer transition-colors">Firmware</span>
            <span className="hover:text-emerald-400 cursor-pointer transition-colors">API Reference</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
