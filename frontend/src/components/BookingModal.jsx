import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Calendar, Clock, User, Phone, Mail, MessageCircle, X } from "lucide-react";
import { useToast } from "../hooks/use-toast";
import { useSiteSettings } from "../hooks/useSiteSettings";
import { getSupportMeta } from "../lib/supportMeta";

export default function BookingModal({ open, onOpenChange }) {
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [step, setStep] = useState('datetime');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
    preferredDate: '',
    preferredTime: '',
    service: 'Free Consultation'
  });
  const { toast } = useToast();
  const { settings } = useSiteSettings();
  const supportMeta = getSupportMeta(settings);
  const queryClient = useQueryClient();

  // Generate dynamic available slots (next 14 business days)
  const generateAvailableSlots = () => {
    const slots = [];
    const today = new Date();
    const businessTimes = ["9:00 AM", "10:30 AM", "12:00 PM", "1:30 PM", "3:00 PM", "4:30 PM"];
    
    for (let i = 1; i <= 14; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      
      // Skip weekends
      if (date.getDay() === 0 || date.getDay() === 6) continue;
      
      const dateString = date.toLocaleDateString('en-AU', { 
        weekday: 'long', 
        month: 'long', 
        day: 'numeric'
      });
      
      slots.push({
        date: dateString,
        dateValue: date.toISOString().split('T')[0],
        times: businessTimes
      });
      
      if (slots.length >= 7) break; // Show 7 business days
    }
    
    return slots;
  };

  // Fetch booked slots to prevent double-booking
  const { data: bookedSlots = [] } = useQuery({
    queryKey: ['/api/booked-slots'],
    queryFn: async () => {
      const response = await fetch('/api/booked-slots');
      if (!response.ok) throw new Error('Failed to fetch booked slots');
      return response.json();
    }
  });

  const availableSlots = generateAvailableSlots().map(slot => ({
    ...slot,
    times: slot.times.filter(time => {
      // Check if this date/time combination is already booked
      const isBooked = bookedSlots.some((booked) => 
        booked.date === slot.dateValue && booked.time === time
      );
      return !isBooked;
    })
  })).filter(slot => slot.times.length > 0); // Remove slots with no available times

  // Submit booking mutation
  const submitBooking = useMutation({
    mutationFn: async (data) => {
      const response = await fetch('/api/contact/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fullName: data.name,
          email: data.email,
          phone: data.phone,
          message: `CONSULTATION BOOKING\n\nPreferred Date: ${data.preferredDate}\nPreferred Time: ${data.preferredTime}\n\nCompany: ${data.company}\nService: ${data.service}\n\nMessage: ${data.message}`,
          status: 'new'
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit booking');
      }
      
      return response.json();
    },
    onSuccess: () => {
      setStep('confirmation');
      // Invalidate queries to refresh available slots and contact inquiries
      queryClient.invalidateQueries({ queryKey: ['/api/booked-slots'] });
      queryClient.invalidateQueries({ queryKey: ['/api/contact-inquiries'] });
      toast({
        title: "Booking Submitted Successfully!",
        description: supportMeta.responseConfirmation,
      });
    },
    onError: () => {
      toast({
        title: "Booking Failed",
        description: "Please try again or contact us directly.",
        variant: "destructive",
      });
    },
  });

  const handleTimeSelect = (date, time, dateValue) => {
    setSelectedDate(date);
    setSelectedTime(time);
    setFormData(prev => ({
      ...prev,
      preferredDate: dateValue,
      preferredTime: time
    }));
    setStep('contact');
  };

  const handleBooking = async () => {
    if (!formData.name || !formData.email) {
      toast({
        title: "Missing Information",
        description: "Please fill in your name and email address.",
        variant: "destructive",
      });
      return;
    }

    await submitBooking.mutateAsync(formData);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const resetModal = () => {
    setStep('datetime');
    setSelectedDate("");
    setSelectedTime("");
  };

  const handleClose = () => {
    onOpenChange(false);
    setTimeout(resetModal, 300); // Reset after modal closes
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[min(95vw,1040px)] max-w-4xl border-none bg-transparent p-0 shadow-none">
        <div className="max-h-[90vh] overflow-y-auto rounded-[32px] border border-white/50 bg-white shadow-[0_35px_90px_rgba(15,23,42,0.35)]">
          <DialogHeader className="p-6 pb-0">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <DialogTitle className="text-2xl font-bold text-black">
                  Book Free Consultation
                </DialogTitle>
                <DialogDescription className="text-gray-600 text-sm mt-1">
                  30-min call with our AI experts • {supportMeta.responseMessage}
                </DialogDescription>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClose}
                className="h-8 w-8 p-0 -mt-1"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </DialogHeader>

          {step === 'datetime' && (
            <div className="space-y-4 px-6 pb-6">
              <div className="flex items-start gap-3 p-3 bg-[#f9cb07]/10 rounded-lg">
                <Calendar className="text-[#f9cb07] h-5 w-5 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-black text-sm">What to Expect</h3>
                  <p className="text-xs text-gray-600 mt-1">
                    • Personalized demo of our AI solutions<br/>
                    • Discussion of your business needs<br/>
                    • Transparent pricing and timeline
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-base font-semibold text-black mb-3">Select Date & Time</h3>
                <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
                  {availableSlots.map((slot, dateIndex) => (
                    <div key={dateIndex} className="border rounded-lg p-3">
                      <h4 className="font-medium text-black text-sm mb-2">{slot.date}</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {slot.times.map((time, timeIndex) => (
                          <Button
                            key={timeIndex}
                            variant="outline"
                            size="sm"
                            className={`text-xs h-8 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black ${
                              selectedDate === slot.date && selectedTime === time
                                ? 'bg-[#f9cb07] text-black'
                                : ''
                            }`}
                            onClick={() => handleTimeSelect(slot.date, time, slot.dateValue)}
                          >
                            <Clock className="w-3 h-3 mr-1" />
                            {time}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="text-center text-xs text-gray-500">
                All times in Australian Eastern Standard Time (AEST)
              </div>
            </div>
          )}

          {step === 'contact' && (
            <div className="space-y-4 px-6 pb-6">
              <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 text-green-700">
                  <Calendar className="w-4 h-4" />
                  <span className="font-medium text-sm">{selectedDate} at {selectedTime}</span>
                </div>
              </div>

              <div>
                <h3 className="text-base font-semibold text-black mb-3">Your Contact Information</h3>
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="name" className="text-xs font-medium text-gray-700">
                      Full Name *
                    </Label>
                    <div className="relative mt-1">
                      <User className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
                      <Input
                        id="name"
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        className="pl-9 h-9 text-sm focus:ring-1 focus:ring-[#f9cb07] focus:border-[#f9cb07]"
                        placeholder="Your full name"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="email" className="text-xs font-medium text-gray-700">
                      Email *
                    </Label>
                    <div className="relative mt-1">
                      <Mail className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className="pl-9 h-9 text-sm focus:ring-1 focus:ring-[#f9cb07] focus:border-[#f9cb07]"
                        placeholder="you@company.com"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="phone" className="text-xs font-medium text-gray-700">
                      Phone *
                    </Label>
                    <div className="relative mt-1">
                      <Phone className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-3.5 h-3.5" />
                      <Input
                        id="phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="pl-9 h-9 text-sm focus:ring-1 focus:ring-[#f9cb07] focus:border-[#f9cb07]"
                        placeholder="+61 400 000 000"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="company" className="text-xs font-medium text-gray-700">
                      Company (Optional)
                    </Label>
                    <Input
                      id="company"
                      type="text"
                      value={formData.company}
                      onChange={(e) => handleInputChange('company', e.target.value)}
                      className="mt-1 h-9 text-sm focus:ring-1 focus:ring-[#f9cb07] focus:border-[#f9cb07]"
                      placeholder="Company name"
                    />
                  </div>

                  <div>
                    <Label className="text-xs font-medium text-gray-700 mb-1.5 block">
                      Interested In? *
                    </Label>
                    <div className="grid grid-cols-3 gap-2">
                      {['AI Chatbots', 'Voice Agents', 'Web Dev'].map((service) => (
                        <Button
                          key={service}
                          type="button"
                          variant="outline"
                          size="sm"
                          className={`text-xs h-8 border-[#f9cb07] text-[#f9cb07] hover:bg-[#f9cb07] hover:text-black ${
                            formData.service === service ? 'bg-[#f9cb07] text-black' : ''
                          }`}
                          onClick={() => handleInputChange('service', service)}
                        >
                          {service}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="message" className="text-xs font-medium text-gray-700">
                      Your Needs (Optional)
                    </Label>
                    <Textarea
                      id="message"
                      rows={2}
                      value={formData.message}
                      onChange={(e) => handleInputChange('message', e.target.value)}
                      className="mt-1 text-sm focus:ring-1 focus:ring-[#f9cb07] focus:border-[#f9cb07] resize-none"
                      placeholder="Briefly describe how AI could help..."
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setStep('datetime')}
                  size="sm"
                  className="flex-1 h-9"
                >
                  Back
                </Button>
                <Button
                  onClick={handleBooking}
                  disabled={submitBooking.isPending || !formData.name || !formData.email || !formData.phone}
                  size="sm"
                  className="flex-1 h-9 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold disabled:opacity-50"
                >
                  {submitBooking.isPending ? 'Submitting...' : 'Confirm Booking'}
                </Button>
              </div>
            </div>
          )}

          {step === 'confirmation' && (
            <div className="text-center space-y-4 px-6 pb-6">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <MessageCircle className="w-6 h-6 text-green-600" />
              </div>

              <div>
                <h3 className="text-lg font-bold text-black mb-1">Booking Confirmed!</h3>
                <p className="text-sm text-gray-600">
                  We'll call you at the scheduled time
                </p>
              </div>

              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Date & Time:</span>
                    <span className="font-medium text-black text-right">{selectedDate} at {selectedTime}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium text-black">30 minutes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium text-black">Phone Call</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-left">
                <h4 className="font-semibold text-black text-sm">What's Next?</h4>
                <div className="text-xs text-gray-600 space-y-0.5">
                  <p>• We'll call you at {formData.phone}</p>
                  <p>• Prepare questions about your needs</p>
                  <p>• Have goals ready to discuss</p>
                  <p>• We'll follow up after the call</p>
                </div>
              </div>

              <Button
                onClick={handleClose}
                size="sm"
                className="w-full h-9 bg-gradient-to-r from-[#f9cb07] to-[#ffcd3c] hover:from-[#e6b800] hover:to-[#f9cb07] text-black font-semibold"
              >
                Done
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
