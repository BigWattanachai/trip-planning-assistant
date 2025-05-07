import React, {useEffect} from 'react';
import {useTripPlanning} from '@/context/TripPlanningContext';
import {MapPin, Calendar, Users, Plane} from 'lucide-react';
import {motion} from 'framer-motion';

interface CanvasProps {
    isPlanning: boolean;
}

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



const Canvas: React.FC<CanvasProps> = ({isPlanning}) => {
    const {state} = useTripPlanning();

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
