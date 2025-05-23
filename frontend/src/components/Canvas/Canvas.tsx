import React, {useEffect} from 'react';
import {useTripPlanning} from '@/context/TripPlanningContext';
import {MapPin, Calendar, Users, Plane, MessageSquare, Loader2} from 'lucide-react';
import {motion} from 'framer-motion';

interface CanvasProps {
    isPlanning: boolean;
}

const formatAIResponse = (text: string): JSX.Element => {
    if (!text) return <></>;

    // Split text into paragraphs
    const paragraphs = text.split(/\n\n+/);

    // Process markdown-style formatting
    const processMarkdown = (content: string) => {
        // Handle bold text
        let processed = content.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Handle italic text
        processed = processed.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        return processed;
    };

    // Function to detect and parse tables
    const parseTable = (paragraph: string) => {
        // Check if paragraph contains table-like structure (| character for columns)
        if (!paragraph.includes('|')) return null;

        const lines = paragraph.split('\n').filter(line => line.trim());

        // Ensure we have at least 2 rows (header + data)
        if (lines.length < 2) return null;

        // Check if this is actually a table (most lines should contain |)
        const tableLines = lines.filter(line => line.includes('|'));
        if (tableLines.length < lines.length * 0.7) return null; // 70% of lines should have | to be considered a table

        // Parse header row
        const headerRow = lines[0].split('|').map(cell => cell.trim()).filter(cell => cell);

        // Check for separator row (e.g., |---|---|---|
        let dataStartIndex = 1;
        if (lines[1].match(/^\s*\|[-:\|\s]+\|\s*$/)) {
            dataStartIndex = 2;
        }

        // Parse data rows
        const dataRows = [];
        for (let i = dataStartIndex; i < lines.length; i++) {
            if (lines[i].includes('|')) {
                const row = lines[i].split('|').map(cell => cell.trim()).filter(cell => cell);
                dataRows.push(row);
            }
        }

        return {
            headers: headerRow,
            rows: dataRows
        };
    };

    return (
        <>
            {paragraphs.map((paragraph, index) => {
                // Check if paragraph is a table
                const tableData = parseTable(paragraph);
                if (tableData) {
                    // Determine table type based on content
                    let tableClassName = "travel-table";
                    let tableType = "standard";

                    // Check if it's a budget table
                    if (paragraph.includes('💰') ||
                        paragraph.toLowerCase().includes('ค่าใช้จ่าย') ||
                        paragraph.toLowerCase().includes('งบประมาณ')) {
                        tableClassName += " budget-table";
                        tableType = "budget";
                    }

                    // Check if it's an itinerary table
                    else if (paragraph.includes('🗺️') ||
                             paragraph.includes('วันที่') ||
                             paragraph.includes('ช่วงเวลา')) {
                        tableClassName += " itinerary-table";
                        tableType = "itinerary";
                    }

                    return (
                        <div key={index} className="overflow-x-auto my-6">
                            <div className="text-sm text-gray-500 mb-2">
                                {tableType === "budget" &&
                                    <span className="inline-flex items-center"><span className="mr-1">💰</span> ตารางสรุปค่าใช้จ่าย</span>
                                }
                                {tableType === "itinerary" &&
                                    <span className="inline-flex items-center"><span className="mr-1">🗺️</span> ตารางกำหนดการเดินทาง</span>
                                }
                            </div>
                            <table className={tableClassName}>
                                <thead>
                                    <tr>
                                        {tableData.headers.map((header, i) => (
                                            <th key={i} className="border border-gray-300 px-4 py-2 text-left">
                                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(header) }} />
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {tableData.rows.map((row, rowIndex) => (
                                        <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                            {row.map((cell, cellIndex) => (
                                                <td key={cellIndex} className="border border-gray-300 px-4 py-2">
                                                    <span dangerouslySetInnerHTML={{ __html: processMarkdown(cell) }} />
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    );
                }
                // Check if this is the main header (แผนการเดินทางของคุณ)
                if (paragraph.includes('===== แผนการเดินทางของคุณ =====')) {
                    return (
                        <h2 key={index} className="text-2xl font-bold text-primary-700 mt-6 mb-6 text-center bg-primary-50 py-3 rounded-lg">
                            {paragraph.replace(/=====/g, '').trim()}
                        </h2>
                    );
                }

                // Check if this is a section header (starts with ** and contains emoji)
                if (paragraph.trim().startsWith('**') && paragraph.trim().endsWith('**') && /\p{Emoji}/u.test(paragraph)) {
                    return (
                        <h3 key={index} className="text-xl font-bold text-primary-700 mt-8 mb-4 border-b border-primary-200 pb-2">
                            <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                        </h3>
                    );
                }

                // Check if this is a regular header (starts with **)
                if (paragraph.trim().startsWith('**') && paragraph.trim().endsWith('**')) {
                    return (
                        <h3 key={index} className="text-xl font-bold text-primary-700 mt-6 mb-3">
                            <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                        </h3>
                    );
                }

                // Check if this is a bullet list (starts with *)
                if (paragraph.match(/^\s*\*\s/m)) {
                    const listItems = paragraph.split(/\n/).filter(line => line.trim().startsWith('*'));
                    return (
                        <ul key={index} className="list-disc pl-6 mb-4 space-y-2">
                            {listItems.map((item, i) => {
                                const content = item.replace(/^\s*\*\s/, '');
                                return (
                                    <li key={i} className="text-gray-700">
                                        <span dangerouslySetInnerHTML={{ __html: processMarkdown(content) }} />
                                    </li>
                                );
                            })}
                        </ul>
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
                                                    <div className="font-semibold text-gray-900">
                                                        <span dangerouslySetInnerHTML={{ __html: processMarkdown(content) }} />
                                                    </div>
                                                ) : (
                                                    <p><span dangerouslySetInnerHTML={{ __html: processMarkdown(content.trim()) }} /></p>
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

                // Check if paragraph is about budget (contains 💰 emoji)
                if (paragraph.includes('💰')) {
                    return (
                        <div key={index} className="bg-amber-50 border-l-4 border-amber-300 p-4 my-4 rounded-r-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about warnings or contingency plans (contains ⚠️ emoji)
                if (paragraph.includes('⚠️')) {
                    return (
                        <div key={index} className="bg-blue-50 border-l-4 border-blue-300 p-4 my-4 rounded-r-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about tips (contains 💡 emoji)
                if (paragraph.includes('💡')) {
                    return (
                        <div key={index} className="bg-green-50 border-l-4 border-green-300 p-4 my-4 rounded-r-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about transportation (contains 🧳 emoji)
                if (paragraph.includes('🧳')) {
                    return (
                        <div key={index} className="bg-blue-50 p-4 my-4 rounded-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about accommodation (contains 🏨 emoji)
                if (paragraph.includes('🏨')) {
                    return (
                        <div key={index} className="bg-purple-50 p-4 my-4 rounded-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about food (contains 🍽️ emoji)
                if (paragraph.includes('🍽️')) {
                    return (
                        <div key={index} className="bg-red-50 p-4 my-4 rounded-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Check if paragraph is about itinerary (contains 🗺️ emoji)
                if (paragraph.includes('🗺️')) {
                    return (
                        <div key={index} className="bg-green-50 p-4 my-4 rounded-lg">
                            <p className="text-gray-700">
                                <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                            </p>
                        </div>
                    );
                }

                // Regular paragraph
                return (
                    <p key={index} className="mb-4 text-gray-700">
                        <span dangerouslySetInnerHTML={{ __html: processMarkdown(paragraph) }} />
                    </p>
                );
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
            {renderWelcomeMessage && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8 }}
                    className="h-full flex items-center justify-center"
                >
                    <div className="text-center max-w-2xl mx-auto px-6">
                        <div className="inline-block p-3 bg-blue-100 rounded-full mb-6">
                            <Plane className="w-10 h-10 text-primary-500" />
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to Travel Planner</h2>
                        <p className="text-gray-600 mb-8 text-lg">
                            Start planning your perfect trip by providing your travel details.
                        </p>
                        <p className="text-gray-500 mb-6">
                            เพียงแชทบอกเราที่ช่องด้านขวาว่าอยากเดินทางไปไหน
                            หรือใช้แบบฟอร์มกรอกรายละเอียด จุดหมายปลายทาง วันที่ และงบประมาณของคุณก็ได้ง่ายๆ
                            แล้วการเดินทางของคุณจะเริ่มต้นขึ้นทันที!
                        </p>
                        <div className="w-80 h-80 mx-auto relative">
                            <div className="absolute inset-0 bg-blue-500 rounded-full opacity-10 animate-pulse"></div>
                            <img
                                src="/travel-illustration.svg"
                                alt="Travel planning illustration"
                                className="w-full h-full object-contain relative z-10"
                            />
                        </div>
                    </div>
                </motion.div>
            )}

            {renderChatOnly && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8 }}
                    className="h-full p-8"
                >
                    <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Chat with our Travel Assistant</h2>
                        <p className="text-gray-600 mb-4">
                            You're chatting with our AI travel assistant. When you're ready to plan a trip,
                            just ask about planning a trip to your desired destination.
                        </p>
                    </div>

                    {/* Chat Messages Section */}
                    {state.messages.length > 0 && (
                        <div className="bg-white rounded-2xl shadow-lg p-8">
                            <div className="flex items-center mb-6">
                                <MessageSquare className="w-6 h-6 text-primary-500 mr-3" />
                                <h2 className="text-2xl font-bold text-gray-900">Chat History</h2>
                            </div>
                            <div className="space-y-4">
                                {state.messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`p-4 rounded-lg ${
                                            message.role === 'user'
                                                ? 'bg-primary-50 border-l-4 border-primary-500 ml-8'
                                                : 'bg-gray-50 border-l-4 border-gray-300 mr-8'
                                        }`}
                                    >
                                        <div className="flex items-center mb-2">
                                            <div
                                                className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                                                    message.role === 'user' ? 'bg-primary-500' : 'bg-gray-500'
                                                }`}
                                            >
                                                <span className="text-white text-xs font-bold">
                                                    {message.role === 'user' ? 'You' : 'AI'}
                                                </span>
                                            </div>
                                            <span className="text-xs text-gray-500">
                                                {new Date(message.timestamp).toLocaleString()}
                                            </span>
                                        </div>
                                        <p className="text-gray-700 whitespace-pre-wrap">{message.content}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </motion.div>
            )}

            {renderLoadingMessage && (
                <div className="h-full flex items-center justify-center">
                    <div className="text-center max-w-lg mx-auto p-8 rounded-2xl bg-white shadow-lg">
                        <div className="relative">
                            <Loader2 className="w-16 h-16 text-primary-500 animate-spin mx-auto mb-6" />
                            <div className="absolute inset-0 bg-primary-100 rounded-full opacity-30 scale-150 animate-ping"></div>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-3">Crafting Your Dream Itinerary</h2>
                        <p className="text-gray-600 text-lg mb-4">Our AI agents are collaborating to design your perfect trip experience...</p>
                        <div className="grid grid-cols-3 gap-3 mt-6">
                            <div className="text-center p-2 rounded-lg bg-blue-50">
                                <p className="text-xs text-gray-500">Finding Activities</p>
                                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                                    <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{width: '60%'}}></div>
                                </div>
                            </div>
                            <div className="text-center p-2 rounded-lg bg-amber-50">
                                <p className="text-xs text-gray-500">Researching Dining</p>
                                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                                    <div className="h-full bg-amber-500 rounded-full animate-pulse" style={{width: '40%'}}></div>
                                </div>
                            </div>
                            <div className="text-center p-2 rounded-lg bg-green-50">
                                <p className="text-xs text-gray-500">Planning Routes</p>
                                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                                    <div className="h-full bg-green-500 rounded-full animate-pulse" style={{width: '75%'}}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

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
