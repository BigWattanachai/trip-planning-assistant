import React, {useEffect} from 'react';
import {useTripPlanning} from '@/context/TripPlanningContext';
import {MapPin, Calendar, Users, Plane} from 'lucide-react';
import {motion} from 'framer-motion';
import {Message, TripData, Accommodation} from '@/context/TripPlanningContext';

interface CanvasProps {
    isPlanning: boolean;
}

// Function to parse AI messages and extract trip data
const parseAIResponseToTripData = (messages: Message[]): TripData | null => {
    // Filter to get assistant messages only
    const assistantMessages = messages.filter(msg => msg.role === 'assistant');

    if (assistantMessages.length === 0) return null;

    // Use the most recent assistant message
    const latestMessage = assistantMessages[assistantMessages.length - 1];
    const content = latestMessage.content;

    // Extract destination - look for patterns like "Your Journey to [Destination]" or "travel to [destination]"
    const destinationRegex = /(?:ที่|เที่ยว|ท่องเที่ยว|เดินทาง|จังหวัด|ไป|ที่|เมือง)(?:\s+)([^\s,\.]+)/i;
    const destinationMatch = content.match(destinationRegex);

    // Extract dates
    const dateRegex = /(\d{1,2}[\s-]+\d{1,2}|วันที่\s+\d{1,2}[-\s]+\d{1,2})(?:\s+|\/)([^\s,\.]+)/i;
    const dateMatch = content.match(dateRegex);

    // Extract budget
    const budgetRegex = /(?:งบ|งบประมาณ|ราคา|งบประมาณ|บาท|ค่าใช้จ่าย)(?:\s+)?(\d{1,3}(?:,\d{3})*)/i;
    const budgetMatch = content.match(budgetRegex);

    // Extract activities - find paragraphs starting with numbers or bullet points
    const activitiesRegex = /(?:\*\*\d+\.\s+([^:]+)\*\*:|\*\*([^:]+)\*\*:)/g;
    const activitiesMatches = Array.from(content.matchAll(activitiesRegex));

    // Create the activities array
    const activities = activitiesMatches.map((match, index) => {
        const name = match[1] || match[2];
        // Get the description by looking for text after the activity name until the next pattern
        const startIndex = match.index + match[0].length;
        const nextMatchIndex = index < activitiesMatches.length - 1 ? activitiesMatches[index + 1].index : content.length;
        const description = content.slice(startIndex, nextMatchIndex).trim();

        return {
            id: `activity-${index}`,
            name: name,
            description: description,
            rating: 4.5, // Default value
            openingHours: "9:00 AM - 5:00 PM", // Default value
            imageUrl: `/images/activities/${index + 1}.jpg`, // Default placeholder
            category: "Attraction",
            highlights: extractHighlights(description),
            location: "ตำบลสะปัน อำเภอปัว จังหวัดน่าน", // Default value
            price: "฿100-300", // Default value
            bestTimeToVisit: "ตุลาคม-กุมภาพันธ์" // Default value
        };
    });

    // Create the trip data object
    const tripData: TripData = {
        destination: destinationMatch ? destinationMatch[1] : "น่าน", // Default if not found
        departure: "กรุงเทพ", // Default
        startDate: dateMatch ? dateMatch[1] : "12 สิงหาคม", // Default
        endDate: dateMatch ? "15 สิงหาคม" : "15 สิงหาคม", // Default
        travelers: "2", // Default
        budget: budgetMatch ? budgetMatch[1] : "15,000", // Default
        activities: activities.length > 0 ? activities : createDefaultActivities("น่าน"),
        restaurants: createDefaultRestaurants("น่าน"),
        flights: createDefaultFlights("น่าน"),
        videos: createDefaultVideos("น่าน"),
        accommodations: createDefaultAccommodations("น่าน")
    };

    return tripData;
};

// Helper functions to extract information or create defaults
const extractHighlights = (text: string): string[] => {
    const lines = text.split(/\n/);
    return lines
        .filter(line => line.trim().startsWith('*') || line.trim().match(/^\d+\./))
        .map(line => line.replace(/^\*|\d+\.\s*/, '').trim())
        .filter(line => line.length > 0)
        .slice(0, 3);
};

// Format AI response with beautiful styling
const formatAIResponse = (text: string): JSX.Element => {
    if (!text) return <></>;

    // Split text into paragraphs
    const paragraphs = text.split(/\n\n+/);

    return (
        <>
            {paragraphs.map((paragraph, index) => {
                // Check if this is a header (starts with **)
                if (paragraph.trim().startsWith('**') && paragraph.trim().endsWith('**')) {
                    return (
                        <h3 key={index} className="text-xl font-bold text-primary-700 mt-6 mb-3">
                            {paragraph.replace(/\*\*/g, '')}
                        </h3>
                    );
                }

                // Check if this is a numbered list item
                if (paragraph.match(/^\d+\./)) {
                    const listItems = paragraph.split(/\n/).filter(line => line.trim());
                    return (
                        <div key={index} className="mb-4">
                            {listItems.map((item, i) => {
                                const match = item.match(/^(\d+)\.(.+)/);
                                if (match) {
                                    const [, number, content] = match;
                                    return (
                                        <div key={i} className="flex items-start mb-3">
                                            <div
                                                className="bg-primary-100 rounded-full w-8 h-8 flex items-center justify-center text-primary-700 font-bold mr-3 flex-shrink-0">
                                                {number}
                                            </div>
                                            <div className="flex-1">
                                                {content.includes('**') ? (
                                                    <>
                                                        <div className="font-semibold text-gray-900">
                                                            {content.replace(/^\s*\*\*|\*\*\s*:$/g, '')}
                                                        </div>
                                                    </>
                                                ) : (
                                                    <p>{content.trim()}</p>
                                                )}
                                            </div>
                                        </div>
                                    );
                                }
                                return <p key={i} className="ml-11 text-gray-700">{item}</p>;
                            })}
                        </div>
                    );
                }

                // Check if paragraph mentions budget
                if (paragraph.toLowerCase().includes('งบประมาณ') || paragraph.toLowerCase().includes('บาท')) {
                    return (
                        <div key={index} className="bg-amber-50 border-l-4 border-amber-300 p-4 my-4 rounded-r-lg">
                            <h4 className="font-semibold text-amber-800 mb-2">👧</h4>
                            <p className="text-gray-700">{paragraph}</p>
                        </div>
                    );
                }

                // Check if paragraph is about travel warnings or important notices
                if (paragraph.toLowerCase().includes('ข้อควรระวัง') ||
                    paragraph.toLowerCase().includes('ข้อควรคำนึง') ||
                    paragraph.toLowerCase().includes('หมายเหตุ')) {
                    return (
                        <div key={index} className="bg-blue-50 border-l-4 border-blue-300 p-4 my-4 rounded-r-lg">
                            <h4 className="font-semibold text-blue-800 mb-2">ข้อควรทราบ</h4>
                            <p className="text-gray-700">{paragraph}</p>
                        </div>
                    );
                }

                // Regular paragraph
                return <p key={index} className="mb-4 text-gray-700">{paragraph}</p>;
            })}
        </>
    );
};

const createDefaultActivities = (destination: string) => [
    {
        id: "activity-1",
        name: "น้ำตกสะปัน",
        description: "น้ำตกที่สวยงามและใหญ่ที่สุดในอำเภอสะปัน คุณสามารถเดินป่าศึกษาธรรมชาติและเพลิดเพลินกับความสดชื่นของธรรมชาติได้",
        rating: 4.7,
        openingHours: "8:00 AM - 6:00 PM",
        imageUrl: "/images/activities/1.jpg",
        category: "ธรรมชาติ",
        location: "อำเภอสะปัน จังหวัดน่าน",
        price: "฿20-50",
        highlights: ["เดินป่าศึกษาธรรมชาติ", "ชมน้ำตกที่สวยงาม", "สัมผัสความสดชื่นของธรรมชาติ"],
        bestTimeToVisit: "มิถุนายน-ตุลาคม"
    },
    {
        id: "activity-2",
        name: "ดอยเสมอดาว",
        description: "ถ้าคุณชื่นชอบการชมวิวภูเขาและท้องฟ้าในยามค่ำคืน ดอยเสมอดาวเป็นสถานที่ที่เหมาะสมมาก คุณสามารถกางเต็นท์นอนและชมดาวได้",
        rating: 4.5,
        openingHours: "เปิดตลอดวัน",
        imageUrl: "/images/activities/2.jpg",
        category: "ธรรมชาติ",
        location: "อำเภอปัว จังหวัดน่าน",
        price: "฿100-200",
        highlights: ["ชมวิวภูเขา", "กางเต็นท์ชมดาว", "อากาศเย็นสบาย"],
        bestTimeToVisit: "พฤศจิกายน-กุมภาพันธ์"
    }
];

const createDefaultRestaurants = (destination: string) => [
    {
        id: "restaurant-1",
        name: "ร้านอาหารเฮือนฮังต่อ",
        cuisine: "อาหารเหนือ",
        priceRange: "฿฿",
        rating: 4.6,
        reviewHighlight: "อาหารเหนือรสชาติดั้งเดิม บรรยากาศดี ท่ามกลางธรรมชาติ",
        imageUrl: "/images/restaurants/1.jpg",
        location: "อำเภอปัว จังหวัดน่าน",
        hours: "10:00 AM - 9:00 PM",
        reservationRequired: false,
        specialties: ["แกงฮังเล", "น้ำพริกหนุ่ม", "ลาบหมู"]
    },
    {
        id: "restaurant-2",
        name: "กาแฟบ้านไทลื้อ",
        cuisine: "กาแฟและของว่าง",
        priceRange: "฿",
        rating: 4.8,
        reviewHighlight: "กาแฟรสชาติดีเยี่ยม บรรยากาศเป็นกันเอง วิวสวย",
        imageUrl: "/images/restaurants/2.jpg",
        location: "อำเภอปัว จังหวัดน่าน",
        hours: "7:00 AM - 6:00 PM",
        reservationRequired: false,
        specialties: ["กาแฟดริป", "ขนมไทย", "เค้กโฮมเมด"]
    }
];

const createDefaultFlights = (destination: string) => [
    {
        id: "flight-1",
        airline: "Thai AirAsia",
        flightNumber: "FD3554",
        departure: {
            airport: "ดอนเมือง (DMK)",
            time: "07:10",
            date: "12 สิงหาคม 2024",
            terminal: "2"
        },
        arrival: {
            airport: "น่าน (NNT)",
            time: "08:30",
            date: "12 สิงหาคม 2024",
            terminal: "1"
        },
        duration: "1h 20m",
        price: 1500,
        stops: 0,
        class: "Economy",
        bookingUrl: "https://www.airasia.com",
        layover: "",
        cancellationPolicy: "ไม่สามารถขอเงินคืนได้",
        amenities: ["น้ำหนักสัมภาระ 7 กก.", "อาหารว่างและเครื่องดื่ม (มีค่าใช้จ่าย)"]
    },
    {
        id: "flight-2",
        airline: "Thai AirAsia",
        flightNumber: "FD3555",
        departure: {
            airport: "น่าน (NNT)",
            time: "18:15",
            date: "15 สิงหาคม 2024",
            terminal: "1"
        },
        arrival: {
            airport: "ดอนเมือง (DMK)",
            time: "19:35",
            date: "15 สิงหาคม 2024",
            terminal: "2"
        },
        duration: "1h 20m",
        price: 1700,
        stops: 0,
        class: "Economy",
        bookingUrl: "https://www.airasia.com",
        layover: "",
        cancellationPolicy: "ไม่สามารถขอเงินคืนได้",
        amenities: ["น้ำหนักสัมภาระ 7 กก.", "อาหารว่างและเครื่องดื่ม (มีค่าใช้จ่าย)"]
    }
];

const createDefaultVideos = (destination: string) => [
    {
        id: "video-1",
        title: `เที่ยว${destination} 3 วัน 2 คืน งบไม่เกิน 5,000 บาท`,
        description: `รีวิวเส้นทางท่องเที่ยว${destination} ครบทุกแลนด์มาร์คสำคัญ พร้อมแนะนำร้านอาหารและที่พัก`,
        thumbnail: "/images/videos/1.jpg",
        embedUrl: "https://www.youtube.com/embed/12345",
        duration: "15:30",
        viewCount: "258K",
        likes: "15K",
        channel: "Travel Thailand",
        publishDate: "2023-10-15"
    },
    {
        id: "video-2",
        title: `Hidden Gems in ${destination} - สถานที่เที่ยวสุดลับ`,
        description: `พาทุกคนไปสัมผัสมนต์เสน่ห์ของ${destination} ที่นักท่องเที่ยวทั่วไปอาจไม่รู้จัก`,
        thumbnail: "/images/videos/2.jpg",
        embedUrl: "https://www.youtube.com/embed/67890",
        duration: "12:45",
        viewCount: "124K",
        likes: "8.5K",
        channel: "Local Guide",
        publishDate: "2023-12-03"
    }
];

const createDefaultAccommodations = (destination: string): Accommodation[] => [
    {
        id: "accommodation-1",
        name: "โฮมสเตย์บ้านสะปัน",
        type: "Homestay",
        rating: 4.8,
        reviewCount: 127,
        price: 900,
        priceUnit: "per night",
        amenities: ["Free Wi-Fi", "Air conditioning", "Private bathroom", "Mountain view"],
        imageUrl: "/images/accommodations/1.jpg",
        platform: 'Airbnb' as 'Airbnb',
        bookingUrl: "https://www.airbnb.com",
        location: "บ้านสะปัน อำเภอปัว จังหวัดน่าน",
        description: "โฮมสเตย์สไตล์ล้านนาท่ามกลางขุนเขา เงียบสงบและสวยงาม เจ้าของที่พักเป็นกันเอง",
        distance: "0.5 km from center"
    },
    {
        id: "accommodation-2",
        name: "น่านซีรีนรีสอร์ท",
        type: "Resort",
        rating: 4.6,
        reviewCount: 203,
        price: 1500,
        priceUnit: "per night",
        amenities: ["Free Wi-Fi", "Swimming pool", "Restaurant", "Garden", "Mountain view"],
        imageUrl: "/images/accommodations/2.jpg",
        platform: 'Agoda' as 'Agoda',
        bookingUrl: "https://www.agoda.com",
        location: "อำเภอเมือง จังหวัดน่าน",
        description: "รีสอร์ทที่ตกแต่งด้วยสไตล์ล้านนาร่วมสมัย สระว่ายน้ำและร้านอาหารมีวิวภูเขา",
        distance: "2.3 km from center"
    }
];

const Canvas: React.FC<CanvasProps> = ({isPlanning}) => {
    const {state, dispatch} = useTripPlanning();

    // Add debug logging to help diagnose the issue
    useEffect(() => {
        console.log("Canvas component state:", {
            hasTripData: !!state.tripData,
            isPlanning,
            destination: state.tripData?.destination || "None",
            messagesCount: state.messages.length,
            hasUserMessages: state.messages.some(msg => msg.role === 'user'),
            renderWelcomeMessage: renderWelcomeMessage,
            renderChatOnly: renderChatOnly
        });
    }, [state.tripData, isPlanning, state.messages.length]);

    // Process AI responses and update trip data
    useEffect(() => {
        if (state.messages.length > 0 && !state.tripData && !isPlanning) {
            const extractedTripData = parseAIResponseToTripData(state.messages);
            if (extractedTripData) {
                dispatch({type: 'SET_TRIP_DATA', payload: extractedTripData});
            }
        }
    }, [state.messages, state.tripData, isPlanning, dispatch]);

    // Fade-in animation for sections
    const containerVariants = {
        hidden: {opacity: 0},
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.3
            }
        }
    };

    const itemVariants = {
        hidden: {opacity: 0, y: 20},
        visible: {
            opacity: 1,
            y: 0,
            transition: {duration: 0.6}
        }
    };

    // Define rendering conditions
    // Only show welcome message if no trip data, not planning, and no user messages
    const renderWelcomeMessage = !state.tripData && !isPlanning &&
        (state.messages.length === 0 || (state.messages.length === 1 && state.messages[0].role === 'assistant'));

    const renderLoadingMessage = isPlanning && !state.tripData;
    const renderTripData = !!state.tripData;

    // Show chat messages when there are messages but no trip data and not in planning mode
    const renderChatOnly = !renderWelcomeMessage && !renderLoadingMessage && !renderTripData;

    // Handle direct rendering of AI response when needed
    const getLatestAIMessage = () => {
        const assistantMessages = state.messages.filter(msg => msg.role === 'assistant');
        return assistantMessages.length > 0 ? assistantMessages[assistantMessages.length - 1].content : '';
    };

    return (
        <div className="h-full overflow-y-auto bg-gradient-to-b from-blue-50 to-white">
            {renderTripData && state.tripData && (
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="p-8"
                >
                    {/* AI Response Section */}
                    {state.messages.some(msg => msg.role === 'assistant') && (
                        <motion.div variants={itemVariants}>
                            <div className="mt-10 bg-white rounded-2xl shadow-lg p-8 relative overflow-hidden">
                                <div
                                    className="absolute top-0 right-0 w-64 h-64 bg-primary-100 rounded-full -translate-y-1/2 translate-x-1/4 opacity-70"></div>
                                <div className="flex items-center mb-6 relative z-10">
                                    <div
                                        className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                                        <Plane className="w-6 h-6 text-primary-600"/>
                                    </div>
                                    <div className="ml-4">
                                        <h2 className="text-2xl font-bold text-gray-900">Your Travel Plan</h2>
                                        <p className="text-gray-600">Curated by our AI Travel Assistant</p>
                                    </div>
                                </div>

                                <div className="prose prose-lg max-w-none relative z-10">
                                    <div
                                        className="whitespace-pre-wrap text-gray-700 leading-relaxed custom-ai-content">
                                        {formatAIResponse(getLatestAIMessage())}
                                    </div>

                                    <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        <div className="bg-blue-50 rounded-lg p-4 flex items-center">
                                            <MapPin className="w-5 h-5 text-blue-500 mr-3"/>
                                            <div>
                                                <h3 className="font-medium text-gray-900">สถานที่ท่องเที่ยว</h3>
                                                <p className="text-sm text-gray-600">แลนด์มาร์คที่น่าสนใจ</p>
                                            </div>
                                        </div>

                                        <div className="bg-amber-50 rounded-lg p-4 flex items-center">
                                            <div className="mr-3 text-amber-500 font-bold text-xl">฿</div>
                                            <div>
                                                <h3 className="font-medium text-gray-900">งบประมาณ</h3>
                                                <p className="text-sm text-gray-600">แผนการใช้จ่าย</p>
                                            </div>
                                        </div>

                                        <div className="bg-green-50 rounded-lg p-4 flex items-center">
                                            <Calendar className="w-5 h-5 text-green-500 mr-3"/>
                                            <div>
                                                <h3 className="font-medium text-gray-900">กำหนดการ</h3>
                                                <p className="text-sm text-gray-600">แผนการเดินทางรายวัน</p>
                                            </div>
                                        </div>

                                        <div className="bg-purple-50 rounded-lg p-4 flex items-center">
                                            <Users className="w-5 h-5 text-purple-500 mr-3"/>
                                            <div>
                                                <h3 className="font-medium text-gray-900">บริการพิเศษ</h3>
                                                <p className="text-sm text-gray-600">ข้อมูลเพิ่มเติม</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </motion.div>
            )}
        </div>
    );
};

export default Canvas;
