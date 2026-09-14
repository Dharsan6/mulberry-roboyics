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
import { SpecularButton } from '../components/reactbits/SpecularButton';

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
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans overflow-x-hidden selection:bg-sky-500 selection:text-white scroll-smooth">
      
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
      <header className="fixed top-0 left-0 right-0 h-20 border-b border-slate-200/80 bg-white/85 backdrop-blur-md z-40 transition-all duration-300 shadow-xs">
        <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => scrollTo('home')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center shadow-md shadow-sky-500/25">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-black tracking-tight text-slate-900 hidden sm:block">MULBERRY</span>
          </div>
          <div className="hidden lg:flex items-center space-x-8 text-sm font-semibold text-slate-600">
            <span onClick={() => scrollTo('home')} className={`cursor-pointer transition-colors ${activeSection === 'home' ? 'text-sky-600 font-bold' : 'hover:text-sky-600'}`}>Home</span>
            <span onClick={() => scrollTo('about')} className={`cursor-pointer transition-colors ${activeSection === 'about' ? 'text-sky-600 font-bold' : 'hover:text-sky-600'}`}>About</span>
            <span onClick={() => scrollTo('how-it-works')} className={`cursor-pointer transition-colors ${activeSection === 'how-it-works' ? 'text-sky-600 font-bold' : 'hover:text-sky-600'}`}>How It Works</span>
            <span onClick={() => scrollTo('modules')} className={`cursor-pointer transition-colors ${activeSection === 'modules' ? 'text-sky-600 font-bold' : 'hover:text-sky-600'}`}>Platform</span>
            <span onClick={() => scrollTo('technology')} className={`cursor-pointer transition-colors ${activeSection === 'technology' ? 'text-sky-600 font-bold' : 'hover:text-sky-600'}`}>Technology</span>
          </div>

          <SpecularButton 
            onClick={() => onEnterDashboard()}
            baseColor="#0284c7"
            lineColor="#38bdf8"
            intensity={0.65}
            radius={24}
            className="text-sm px-4 py-2 border border-sky-400/40 shadow-sm"
          >
            <span className="text-white font-semibold">Explore Dashboard</span>
            <ArrowRight className="w-4 h-4 text-sky-100" />
          </SpecularButton>
        </div>
      </header>

      {/* 
        =================
        HERO SECTION (Video + Light Blue GradientWaves)
        =================
      */}
      <section id="home" className="relative min-h-[100vh] flex items-center justify-center pt-20 overflow-hidden bg-slate-900">
        
        {/* Layer 1: Background Video */}
        <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover object-center opacity-65 scale-105 filter brightness-95"
          >
            <source src="/168572-839370257.mp4" type="video/mp4" />
          </video>
        </div>

        {/* Layer 2: Light Blue Gradient Waves */}
        <div className="absolute inset-0 z-10 pointer-events-auto overflow-hidden opacity-75 mix-blend-screen">
          <GradientWaves 
            horizonColor="#bae6fd"
            waveColor="#0ea5e9"
            crestColor="#ffffff"
            speed={0.35}
            amplitude={2.2}
            waveScale={0.55}
            waveRatio={0.9}
            swell={30}
            turbulence={18}
            tilt={1.12}
            zoom={1.05}
            height={5.5}
            fogDepth={16}
            detail="medium"
            brightness={1.1}
            opacity={0.8}
            mouseInteraction={true}
            parallaxStrength={0.4}
            grain={true}
            grainIntensity={0.03}
            className="w-full h-full"
          />
        </div>

        {/* Layer 3: Subtle Light Gradient Scrim for Pristine Readability */}
        <div className="absolute inset-0 z-10 bg-gradient-to-b from-slate-950/40 via-slate-950/20 to-slate-50 pointer-events-none" />

        {/* Hero Content */}
        <div className="relative z-20 max-w-5xl mx-auto px-6 text-center flex flex-col items-center mt-[-6vh]">
          <div className="inline-flex items-center space-x-2 bg-white/90 backdrop-blur-md border border-sky-300 text-sky-700 px-4 py-1.5 rounded-full text-xs font-mono mb-8 font-semibold shadow-md">
            <ShieldCheck className="w-4 h-4 text-sky-600" />
            <span>PRECISION SERICULTURE INTELLIGENCE</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-black tracking-tight text-white mb-6 leading-tight drop-shadow-md">
            Precision Intelligence for <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-300 via-cyan-200 to-teal-300">
              Every Mulberry Field
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-100 max-w-3xl mx-auto mb-10 leading-relaxed drop-shadow">
            Mulberry combines autonomous rover technology, soil sensing, spatial intelligence, and machine learning to turn field measurements into actionable agronomic insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <SpecularButton 
              onClick={() => onEnterDashboard()}
              baseColor="#0284c7"
              lineColor="#38bdf8"
              intensity={0.7}
              radius={9999}
              className="px-8 py-4 font-bold text-lg border border-sky-300/60 shadow-xl shadow-sky-600/30"
            >
              <span className="text-white">Explore Dashboard</span>
              <ArrowRight className="w-5 h-5 text-sky-100" />
            </SpecularButton>

            <button 
              onClick={() => scrollTo('how-it-works')} 
              className="w-full sm:w-auto px-8 py-4 rounded-full bg-white/90 hover:bg-white border border-slate-200 text-slate-800 hover:text-slate-950 font-semibold text-lg flex items-center justify-center space-x-2 transition-all shadow-lg shadow-slate-900/10 hover:shadow-xl backdrop-blur-md"
            >
              <span>How It Works</span>
              <ChevronRight className="w-5 h-5 text-slate-500" />
            </button>
          </div>
        </div>

        {/* Bottom Fade Mask into next section */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent pointer-events-none z-20" />
      </section>

      {/* 
        =================
        ABOUT SECTION 
        =================
      */}
      <section id="about" className="py-24 relative bg-slate-50">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <div className="inline-flex items-center space-x-2 text-sky-600 font-mono text-sm mb-6 font-semibold">
            <Info className="w-4 h-4" />
            <span>THE CHALLENGE</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-6 leading-tight">
            Why Automate Soil Intelligence?
          </h2>
          <p className="text-slate-600 text-lg md:text-xl leading-relaxed mb-8">
            Traditional sericulture relies on manual soil sampling, resulting in sparse data and inaccurate nutrient prescriptions. This leads to over-fertilization, increased costs, and compromised mulberry leaf quality—the primary food source for silkworms.
          </p>
          <div className="p-6 rounded-2xl bg-sky-50 border border-sky-200/80 inline-block text-left shadow-sm">
            <h4 className="text-sky-800 font-bold mb-2 text-base">The Solution</h4>
            <p className="text-slate-700 text-sm max-w-lg leading-relaxed">
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
      <section id="how-it-works" className="py-24 relative bg-white border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-4">The Autonomous Pipeline</h2>
            <p className="text-slate-600 max-w-2xl mx-auto text-lg">From physical field probing to spatial interpolation and actionable nutrient prescriptions.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6 relative">
            {/* Connecting Line (Desktop) */}
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-sky-400/0 via-sky-400/30 to-sky-400/0 -translate-y-1/2 z-0" />

            {[
              { icon: Bot, title: "Autonomous Rover", desc: "4WD robotic platform navigates to specific GPS waypoints in the field." },
              { icon: Activity, title: "Soil Sensing", desc: "Rack-and-pinion deploys NPK/pH/EC sensors via Modbus RS485." },
              { icon: Cpu, title: "Spatial ML", desc: "FastAPI backend runs EfficientNet & IDW for spatial field interpolation." },
              { icon: Droplets, title: "Agronomic Insights", desc: "Actionable prescription maps generated for targeted fertilizer dosing." }
            ].map((step, idx) => (
              <GlareHover key={idx} className="relative z-10 h-full w-full rounded-2xl" scale={1.03}>
                <div className="h-full bg-slate-50/90 border border-slate-200 p-8 rounded-2xl flex flex-col items-center text-center group shadow-sm hover:shadow-md hover:border-sky-300 transition-all">
                  <div className="w-16 h-16 rounded-2xl bg-sky-50 border border-sky-200/70 flex items-center justify-center mb-6 group-hover:border-sky-400 group-hover:bg-sky-100 transition-colors">
                    <step.icon className="w-8 h-8 text-sky-600" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{step.title}</h3>
                  <p className="text-sm text-slate-600">{step.desc}</p>
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
      <section id="modules" className="py-24 relative bg-slate-50 border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-4">Explore the Mulberry Platform</h2>
            <p className="text-slate-600 max-w-2xl mx-auto text-lg">One platform for rover operations, soil intelligence, and agronomic decisions.</p>
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
                  className="h-full cursor-pointer bg-white p-8 rounded-2xl border border-slate-200 hover:border-sky-400 flex flex-col items-start text-left group transition-all duration-300 relative overflow-hidden shadow-sm hover:shadow-xl"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-sky-500/5 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  
                  <div className="relative z-10 w-12 h-12 rounded-xl bg-sky-50 border border-sky-200/80 flex items-center justify-center mb-6 group-hover:bg-sky-500 group-hover:text-white transition-all">
                    <mod.icon className="w-6 h-6 text-sky-600 group-hover:text-white transition-colors" />
                  </div>
                  
                  <h3 className="relative z-10 text-xl font-bold text-slate-900 mb-3 group-hover:text-sky-600 transition-colors">{mod.title}</h3>
                  <p className="relative z-10 text-sm text-slate-600 mb-6 flex-1 leading-relaxed">{mod.desc}</p>
                  
                  <div className="relative z-10 flex items-center space-x-2 text-xs font-bold tracking-wider text-sky-600 opacity-0 group-hover:opacity-100 transform translate-x-[-10px] group-hover:translate-x-0 transition-all duration-300">
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
      <section id="technology" className="py-24 relative bg-white border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            
            <div>
              <div className="inline-flex items-center space-x-2 text-sky-600 font-mono text-sm mb-6 font-semibold">
                <Database className="w-4 h-4" />
                <span>TECH STACK & ARCHITECTURE</span>
              </div>
              <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-6 leading-tight">
                Engineered for <br/>
                <span className="text-sky-600">Field Accuracy</span>
              </h2>
              <p className="text-slate-600 text-lg mb-8 leading-relaxed">
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
                     <div className="mt-1 w-6 h-6 rounded-full bg-sky-100 flex items-center justify-center shrink-0">
                      <div className="w-2 h-2 rounded-full bg-sky-600" />
                    </div>
                    <div>
                      <h4 className="text-slate-900 font-bold mb-1">{item.title}</h4>
                      <p className="text-sm text-slate-600">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-r from-sky-400/20 to-blue-500/20 blur-3xl opacity-50 pointer-events-none rounded-[3rem]" />
              <div className="relative bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-2xl">
                {/* Simulated Code/Tech visual */}
                <div className="bg-slate-950 rounded-2xl border border-slate-800 p-4 font-mono text-xs sm:text-sm overflow-hidden text-slate-400 h-[400px] flex flex-col">
                  <div className="flex space-x-2 mb-4 pb-4 border-b border-slate-800">
                    <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                    <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  </div>
                  <div className="flex-1 overflow-y-auto opacity-80 select-none">
                    <p className="text-sky-400 mb-2"># FastAPI Telemetry Ingestion</p>
                    <p><span className="text-pink-400">@app.post</span>(<span className="text-amber-300">"/api/telemetry"</span>)</p>
                    <p><span className="text-purple-400">async def</span> <span className="text-blue-400">ingest_telemetry</span>(telemetry: TelemetryModel):</p>
                    <p className="ml-4">logger.info(<span className="text-amber-300">f"Received payload from WP: {'{telemetry.waypoint_id}'}"</span>)</p>
                    <p className="ml-4">db.insert(telemetry)</p>
                    <p className="ml-4 text-sky-400"># Trigger inference pipeline</p>
                    <p className="ml-4">features = extract_spatial_features(telemetry)</p>
                    <p className="ml-4">prediction = efficientnet_model.predict(features)</p>
                    <br/>
                    <p className="text-sky-400 mb-2"># State Machine Step</p>
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
        SOIL INTELLIGENCE SECTION 
        =================
      */}
      <section id="intelligence" className="py-24 relative bg-slate-50 border-t border-slate-200/80">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="inline-flex items-center space-x-2 text-sky-600 font-mono text-sm mb-6 font-semibold">
            <Globe className="w-4 h-4" />
            <span>ACTIONABLE DATA</span>
          </div>
          <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-6">Deep Soil Intelligence</h2>
          <p className="text-slate-600 max-w-2xl mx-auto text-lg mb-16">
            Mulberry converts raw telemetry into visual, actionable health metrics. Monitor pH, moisture, electrical conductivity, and N-P-K levels across your entire plantation.
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
            {[
              { label: "Nitrogen (N)", val: "Deficit", color: "text-rose-700", bg: "bg-rose-50", border: "border-rose-200" },
              { label: "Phosphorus (P)", val: "Optimal", color: "text-emerald-700", bg: "bg-emerald-50", border: "border-emerald-200" },
              { label: "pH Level", val: "6.9", color: "text-sky-700", bg: "bg-sky-50", border: "border-sky-200" },
              { label: "Moisture", val: "42%", color: "text-blue-700", bg: "bg-blue-50", border: "border-blue-200" },
            ].map((stat, i) => (
              <div key={i} className={`bg-white p-6 rounded-2xl border ${stat.border} shadow-sm flex flex-col items-center justify-center`}>
                <span className="text-slate-500 text-sm font-semibold mb-2">{stat.label}</span>
                <span className={`text-2xl font-black ${stat.color} ${stat.bg} px-4 py-1 rounded-lg border ${stat.border}`}>{stat.val}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 
        =================
        DASHBOARD CTA PREVIEW 
        =================
      */}
      <section className="py-24 relative bg-slate-100/90 border-t border-slate-200 overflow-hidden pb-48">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-sky-200/40 via-slate-100 to-slate-100 pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-6 relative z-10 flex flex-col items-center text-center">
          <h2 className="text-3xl md:text-5xl font-black text-slate-900 mb-6">From Field Data to Actionable Intelligence</h2>
          <p className="text-slate-600 text-lg mb-12 max-w-xl">
            Access the Precision Sericulture Dashboard to monitor rover telemetry, view spatial ML heatmaps, and generate targeted fertilizer prescriptions.
          </p>

          <GlareHover scale={1.02} className="w-full max-w-4xl rounded-[2.5rem]">
            <div 
              onClick={() => onEnterDashboard()}
              className="cursor-pointer group relative rounded-[2.5rem] p-2 bg-gradient-to-b from-slate-700 to-slate-900 shadow-2xl shadow-sky-900/20 border border-slate-700/50 overflow-hidden"
            >
              {/* Simulated Dashboard UI Frame */}
              <div className="bg-slate-950 rounded-[2rem] border border-slate-800 h-auto min-h-[500px] overflow-hidden relative">
                
                <div className="absolute inset-0 flex items-center justify-center z-20 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm">
                  <div className="px-8 py-4 bg-sky-500 hover:bg-sky-400 text-white font-bold rounded-full flex items-center space-x-3 transform translate-y-4 group-hover:translate-y-0 transition-transform shadow-xl">
                    <span>Explore Dashboard &rarr;</span>
                  </div>
                </div>

                <div className="h-14 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-900/50">
                  <div className="flex items-center space-x-2 text-sky-400 font-bold text-sm tracking-wide">
                    <LayoutDashboard className="w-4 h-4" />
                    <span>DASHBOARD OVERVIEW</span>
                  </div>
                  <div className="flex space-x-3">
                    <div className="text-xs font-mono text-slate-400 bg-slate-800 px-3 py-1 rounded-full flex items-center space-x-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <span>SYSTEM LIVE</span>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 grid grid-cols-1 md:grid-cols-4 gap-6 text-left">
                  <div className="md:col-span-3 space-y-6">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">Total Samples</div>
                        <div className="text-2xl font-black text-white">1,248</div>
                      </div>
                      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">Avg Soil pH</div>
                        <div className="text-2xl font-black text-sky-400">6.8</div>
                      </div>
                      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                        <div className="text-slate-400 text-xs font-semibold mb-1 uppercase">N-P-K Status</div>
                        <div className="text-2xl font-black text-teal-400">Optimal</div>
                      </div>
                    </div>
                    <div className="h-48 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col justify-between">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-slate-300 font-semibold text-sm">Moisture Trend (7 Days)</span>
                        <span className="text-sky-400 text-xs font-bold bg-sky-500/10 px-2 py-1 rounded">+2.4%</span>
                      </div>
                      <div className="flex items-end justify-between h-full pt-4 space-x-2">
                        {[40, 55, 45, 70, 65, 80, 75].map((h, i) => (
                          <div key={i} style={{ height: `${h}%` }} className="w-full bg-sky-500/30 hover:bg-sky-500/50 transition-colors rounded-t-sm relative group">
                            <div className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 text-xs text-white bg-slate-800 px-2 rounded transition-opacity">
                              {h}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-6">
                    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                      <div className="text-slate-400 text-xs font-semibold mb-3 uppercase">Rover State</div>
                      <div className="flex items-center space-x-3 mb-2">
                        <Bot className="w-8 h-8 text-sky-400" />
                        <div>
                          <div className="text-white font-bold text-sm">IDLE (CHARGING)</div>
                          <div className="text-slate-400 text-xs">Battery: 98%</div>
                        </div>
                      </div>
                    </div>
                    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 space-y-4">
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
      <footer className="border-t border-slate-200 bg-white py-12 pb-32">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-sm text-slate-500">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Bot className="w-5 h-5 text-sky-600 opacity-80" />
            <span className="text-slate-600 font-medium">© 2026 Mulberry Precision Sericulture Project</span>
          </div>
          <div className="flex items-center space-x-6">
            <span className="hover:text-sky-600 cursor-pointer transition-colors">Documentation</span>
            <span className="hover:text-sky-600 cursor-pointer transition-colors">Firmware</span>
            <span className="hover:text-sky-600 cursor-pointer transition-colors">API Reference</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
