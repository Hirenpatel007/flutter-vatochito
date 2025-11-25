import 'package:emoji_picker_flutter/emoji_picker_flutter.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';
import 'package:vatochito_chat/src/features/auth/data/models/user_model.dart';
import 'package:vatochito_chat/src/features/chat/data/models/message_model.dart';
// import 'package:file_picker/file_picker.dart';  // Commented out temporarily

import 'package:vatochito_chat/src/features/chat/presentation/bloc/chat_room_cubit.dart';

import '../../../../../../screens/call_page.dart';
import '../widgets/message_bubble.dart';

class ChatRoomPage extends StatefulWidget {
  const ChatRoomPage(
      {super.key, required this.conversationId, this.title, this.currentUser});

  final int conversationId;
  final String? title;
  final UserModel? currentUser;

  @override
  State<ChatRoomPage> createState() => _ChatRoomPageState();
}

class _ChatRoomPageState extends State<ChatRoomPage>
    with TickerProviderStateMixin {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  final _focusNode = FocusNode();
  bool _isEmojiPickerVisible = false;
  bool _isAttachmentMenuVisible = false;
  late AnimationController _attachmentAnimationController;
  int? _editingMessageId;

  @override
  void initState() {
    super.initState();
    context.read<ChatRoomCubit>().connect(widget.conversationId);
    _attachmentAnimationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _focusNode.dispose();
    _attachmentAnimationController.dispose();
    super.dispose();
  }

  void _toggleEmojiPicker() {
    _focusNode.unfocus();
    setState(() {
      _isEmojiPickerVisible = !_isEmojiPickerVisible;
      _isAttachmentMenuVisible = false;
    });
  }

  void _toggleAttachmentMenu() {
    _focusNode.unfocus();
    setState(() {
      _isAttachmentMenuVisible = !_isAttachmentMenuVisible;
      _isEmojiPickerVisible = false;
      if (_isAttachmentMenuVisible) {
        _attachmentAnimationController.forward();
      } else {
        _attachmentAnimationController.reverse();
      }
    });
  }

  void _sendMessage() {
    print('DEBUG: _sendMessage called');
    print('DEBUG: Message text: "${_messageController.text}"');
    print('DEBUG: Conversation ID: ${widget.conversationId}');
    if (_messageController.text.isNotEmpty) {
      if (_editingMessageId != null) {
        print('DEBUG: Editing message');
        context.read<ChatRoomCubit>().editMessage(
              _editingMessageId!,
              _messageController.text,
              widget.conversationId,
            );
        setState(() {
          _editingMessageId = null;
        });
      } else {
        print('DEBUG: Sending new message');
        context
            .read<ChatRoomCubit>()
            .sendMessage(_messageController.text, widget.conversationId);
      }
      _messageController.clear();
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    } else {
      print('DEBUG: Message is empty, not sending');
    }
  }

  void _showMessageOptions(BuildContext context, MessageModel message) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text('Edit'),
                onTap: () {
                  Navigator.pop(context);
                  _editMessage(message);
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete, color: Colors.red),
                title:
                    const Text('Delete', style: TextStyle(color: Colors.red)),
                onTap: () {
                  Navigator.pop(context);
                  _deleteMessage(message);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _editMessage(MessageModel message) {
    setState(() {
      _editingMessageId = message.id;
      _messageController.text = message.content;
    });
    _focusNode.requestFocus();
  }

  void _deleteMessage(MessageModel message) {
    context
        .read<ChatRoomCubit>()
        .deleteMessage(message.id, widget.conversationId);
  }

  void _cancelEdit() {
    setState(() {
      _editingMessageId = null;
      _messageController.clear();
    });
    _focusNode.unfocus();
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);
    if (pickedFile != null) {
      // Handle image file
    }
    _toggleAttachmentMenu();
  }

  // Future<void> _pickFile() async {
  //   final result = await FilePicker.platform.pickFiles();
  //   if (result != null) {
  //     // Handle generic file
  //   }
  //   _toggleAttachmentMenu();
  // }

  void _startCall(bool isVideoCall) {
    if (widget.currentUser == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User information missing')),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CallPage(
          callID: widget.conversationId.toString(),
          userID: widget.currentUser!.id.toString(),
          userName: widget.currentUser!.username,
          isVideoCall: isVideoCall,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title ?? 'Chat'),
        actions: [
          IconButton(
            icon: const Icon(Icons.call),
            onPressed: () => _startCall(false),
          ),
          IconButton(
            icon: const Icon(Icons.videocam),
            onPressed: () => _startCall(true),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: BlocConsumer<ChatRoomCubit, ChatRoomState>(
              listener: (context, state) {
                if (state.errorMessage != null) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(state.errorMessage!)),
                  );
                  // Clear error after showing
                  Future.delayed(const Duration(milliseconds: 100), () {
                    context.read<ChatRoomCubit>().clearError();
                  });
                }
              },
              builder: (context, state) {
                if (state.status == ChatRoomStatus.loading &&
                    state.messages.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (state.status == ChatRoomStatus.failure) {
                  return Center(
                    child:
                        Text(state.errorMessage ?? 'Failed to load messages'),
                  );
                }
                return ListView.builder(
                  controller: _scrollController,
                  reverse: true,
                  itemCount: state.messages.length,
                  itemBuilder: (context, index) {
                    final message = state.messages[index];
                    final isMe = message.user.id == widget.currentUser?.id;
                    return GestureDetector(
                      onLongPress: isMe && !message.isDeleted
                          ? () => _showMessageOptions(context, message)
                          : null,
                      child: MessageBubble(message: message, isMe: isMe),
                    );
                  },
                );
              },
            ),
          ),
          if (_editingMessageId != null)
            Container(
              color: Colors.grey[200],
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  const Icon(Icons.edit, size: 16),
                  const SizedBox(width: 8),
                  const Text('Editing message'),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, size: 16),
                    onPressed: _cancelEdit,
                  ),
                ],
              ),
            ),
          _buildMessageInput(),
          _buildEmojiPicker(),
          _buildAttachmentMenu(),
        ],
      ),
    );
  }

  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 5,
          ),
        ],
      ),
      child: Row(
        children: [
          IconButton(
            icon: Icon(
              _isEmojiPickerVisible
                  ? Icons.keyboard
                  : Icons.emoji_emotions_outlined,
            ),
            onPressed: _toggleEmojiPicker,
          ),
          IconButton(
            icon: const Icon(Icons.attach_file),
            onPressed: _toggleAttachmentMenu,
          ),
          Expanded(
            child: TextField(
              controller: _messageController,
              focusNode: _focusNode,
              decoration: const InputDecoration(
                hintText: 'Type a message',
                border: InputBorder.none,
                contentPadding: EdgeInsets.symmetric(horizontal: 16),
              ),
              onTap: () {
                if (_isEmojiPickerVisible || _isAttachmentMenuVisible) {
                  setState(() {
                    _isEmojiPickerVisible = false;
                    _isAttachmentMenuVisible = false;
                    _attachmentAnimationController.reverse();
                  });
                }
              },
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: _sendMessage,
          ),
        ],
      ),
    );
  }

  Widget _buildEmojiPicker() {
    return Offstage(
      offstage: !_isEmojiPickerVisible,
      child: SizedBox(
        height: 250,
        child: EmojiPicker(
          onEmojiSelected: (category, emoji) {
            _messageController
              ..text += emoji.emoji
              ..selection = TextSelection.fromPosition(
                TextPosition(offset: _messageController.text.length),
              );
          },
          config: const Config(
            columns: 7,
            emojiSizeMax: 32 * (1.0),
            verticalSpacing: 0,
            horizontalSpacing: 0,
            gridPadding: EdgeInsets.zero,
            initCategory: Category.RECENT,
            bgColor: Color(0xFFF2F2F2),
            indicatorColor: Colors.blue,
            iconColor: Colors.grey,
            iconColorSelected: Colors.blue,
            backspaceColor: Colors.blue,
            skinToneDialogBgColor: Colors.white,
            skinToneIndicatorColor: Colors.grey,
            enableSkinTones: true,
            recentTabBehavior: RecentTabBehavior.RECENT,
            recentsLimit: 28,
            noRecents: Text(
              'No Recents',
              style: TextStyle(fontSize: 20, color: Colors.black26),
              textAlign: TextAlign.center,
            ),
            loadingIndicator: SizedBox.shrink(),
            tabIndicatorAnimDuration: kTabScrollDuration,
            categoryIcons: CategoryIcons(),
            buttonMode: ButtonMode.MATERIAL,
          ),
        ),
      ),
    );
  }

  Widget _buildAttachmentMenu() {
    return SizeTransition(
      sizeFactor: CurvedAnimation(
        parent: _attachmentAnimationController,
        curve: Curves.easeInOut,
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        color: Theme.of(context).cardColor.withOpacity(0.95),
        child: GridView.count(
          crossAxisCount: 4,
          shrinkWrap: true,
          children: [
            _buildAttachmentMenuItem(
              icon: Icons.camera_alt,
              label: 'Camera',
              onTap: () => _pickImage(ImageSource.camera),
            ),
            _buildAttachmentMenuItem(
              icon: Icons.photo_library,
              label: 'Gallery',
              onTap: () => _pickImage(ImageSource.gallery),
            ),
            // _buildAttachmentMenuItem(
            //   icon: Icons.insert_drive_file,
            //   label: 'Document',
            //   onTap: _pickFile,
            // ),
          ],
        ),
      ),
    );
  }

  Widget _buildAttachmentMenuItem({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 30),
          const SizedBox(height: 8),
          Text(label),
        ],
      ),
    );
  }
}
